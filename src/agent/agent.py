"""エージェントの基底クラスを定義するモジュール."""

from __future__ import annotations

import os
import random
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from jinja2 import Template
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage

from aiwolf_nlp_common.packet import Info, Packet, Request, Role, Setting, Status, Talk

from utils.agent_logger import AgentLogger

if TYPE_CHECKING:
    from collections.abc import Callable


class Agent:
    """エージェントの基底クラス."""

    def __init__(
        self,
        config: dict,
        name: str,
        game_id: str,
        role: Role,
    ) -> None:
        """エージェントの初期化を行う."""
        self.config = config
        self.agent_name = name
        self.agent_logger = AgentLogger(config, name, game_id)
        self.request: Request | None = None
        self.info: Info | None = None
        self.setting: Setting | None = None
        self.talk_history: list[Talk] = []
        self.whisper_history: list[Talk] = []
        self.role = role

        self.sent_talk_count: int = 0
        self.sent_whisper_count: int = 0
        self.llm_model: BaseChatModel | None = None
        self.llm_message_history: list[BaseMessage] = []

        load_dotenv(dotenv_path="./../../config/.env")

    @staticmethod
    def timeout(func: Callable) -> Callable:
        """アクションタイムアウトを設定するデコレータ."""

        def _wrapper(self: Agent, *args, **kwargs) -> str:  # noqa: ANN002, ANN003
            res = ""

            def execute_with_timeout() -> None:
                nonlocal res
                try:
                    res = func(self, *args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    res = e

            thread = Thread(target=execute_with_timeout, daemon=True)
            thread.start()

            timeout_value = (self.setting.timeout.action if self.setting else 0) // 1000
            if timeout_value > 0:
                thread.join(timeout=timeout_value)
                if thread.is_alive():
                    self.agent_logger.logger.warning(
                        "アクションがタイムアウトしました: %s",
                        self.request,
                    )
            else:
                thread.join()

            if isinstance(res, Exception):
                raise res

            return res

        return _wrapper

    def set_packet(self, packet: Packet) -> None:
        """パケット情報をセットする."""
        self.request = packet.request
        if packet.info:
            self.info = packet.info
        if packet.setting:
            self.setting = packet.setting
        if packet.talk_history:
            self.talk_history.extend(packet.talk_history)
        if packet.whisper_history:
            self.whisper_history.extend(packet.whisper_history)
        if self.request == Request.INITIALIZE:
            self.talk_history: list[Talk] = []
            self.whisper_history: list[Talk] = []
            self.llm_message_history: list[BaseMessage] = []
        self.agent_logger.logger.debug(packet)

    def get_alive_agents(self) -> list[str]:
        """生存しているエージェントのリストを取得する."""
        if not self.info:
            return []
        return [k for k, v in self.info.status_map.items() if v == Status.ALIVE]

    def _send_message_to_llm(self, request: Request | None) -> str | None:
        if request is None:
            return None
        if request.lower() not in self.config["prompt"]:
            return None
        prompt = self.config["prompt"][request.lower()]
        if float(self.config["llm"]["sleep_time"]) > 0:
            sleep(float(self.config["llm"]["sleep_time"]))
        key = {
            "info": self.info,
            "setting": self.setting,
            "talk_history": self.talk_history,
            "whisper_history": self.whisper_history,
            "role": self.role,
            "sent_talk_count": self.sent_talk_count,
            "sent_whisper_count": self.sent_whisper_count,
        }
        template: Template = Template(prompt)
        prompt = template.render(**key).strip()
        if self.llm_model is None:
            self.agent_logger.logger.error("LLM is not initialized")
            return None
        try:
            self.llm_message_history.append(HumanMessage(content=prompt))
            response = self.llm_model.invoke(self.llm_message_history)
            response_content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content[0])
            )
            self.llm_message_history.append(AIMessage(content=response_content))
            self.agent_logger.logger.info(["LLM", prompt, response_content])
        except Exception:
            self.agent_logger.logger.exception("Failed to send message to LLM")
            return None
        else:
            return response_content

    @timeout
    def name(self) -> str:
        """名前リクエストに対する応答を返す."""
        return self.agent_name

    def initialize(self) -> None:
        """ゲーム開始リクエストに対する初期化処理を行う."""
        if self.config is None or self.info is None:
            return

        model_type = str(self.config["llm"]["type"])
        match model_type:
            case "openai":
                self.llm_model = ChatOpenAI(
                    model=str(self.config["openai"]["model"]),
                    temperature=float(self.config["openai"]["temperature"]),
                    api_key=SecretStr(os.environ["OPENAI_API_KEY"]),
                )
            case "google":
                self.llm_model = ChatGoogleGenerativeAI(
                    model=str(self.config["google"]["model"]),
                    temperature=float(self.config["google"]["temperature"]),
                    api_key=SecretStr(os.environ["GOOGLE_API_KEY"]),
                )
            case "ollama":
                self.llm_model = ChatOllama(
                    model=str(self.config["ollama"]["model"]),
                    temperature=float(self.config["ollama"]["temperature"]),
                    base_url=str(self.config["ollama"]["base_url"]),
                )
            case _:
                raise ValueError(model_type, "Unknown LLM type")
        self._send_message_to_llm(self.request)

    def daily_initialize(self) -> None:
        """昼開始リクエストに対する処理を行う."""
        self._send_message_to_llm(self.request)

    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        response = self._send_message_to_llm(self.request)
        self.sent_whisper_count = len(self.whisper_history)
        return response or ""

    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        response = self._send_message_to_llm(self.request)
        self.sent_talk_count = len(self.talk_history)
        return response or ""

    def daily_finish(self) -> None:
        """昼終了リクエストに対する処理を行う."""
        self._send_message_to_llm(self.request)

    def divine(self) -> str:
        """占いリクエストに対する応答を返す."""
        return self._send_message_to_llm(self.request) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    def guard(self) -> str:
        """護衛リクエストに対する応答を返す."""
        return self._send_message_to_llm(self.request) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        return self._send_message_to_llm(self.request) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    def attack(self) -> str:
        """襲撃リクエストに対する応答を返す."""
        return self._send_message_to_llm(self.request) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    def finish(self) -> None:
        """ゲーム終了リクエストに対する処理を行う."""

    @timeout
    def action(self) -> str | None:  # noqa: C901, PLR0911
        """リクエストの種類に応じたアクションを実行する."""
        match self.request:
            case Request.NAME:
                return self.name()
            case Request.TALK:
                return self.talk()
            case Request.WHISPER:
                return self.whisper()
            case Request.VOTE:
                return self.vote()
            case Request.DIVINE:
                return self.divine()
            case Request.GUARD:
                return self.guard()
            case Request.ATTACK:
                return self.attack()
            case Request.INITIALIZE:
                self.initialize()
            case Request.DAILY_INITIALIZE:
                self.daily_initialize()
            case Request.DAILY_FINISH:
                self.daily_finish()
            case Request.FINISH:
                self.finish()
        return None
