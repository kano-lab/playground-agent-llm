"""エージェントの基底クラスを定義するモジュール."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from utils.timeout import timeout

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage

import random

from aiwolf_nlp_common.packet import Info, Packet, Request, Role, Setting, Status, Talk

from utils.agent_logger import AgentLogger


class Agent:
    """エージェントの基底クラス."""

    def __init__(
        self,
        config: dict,
        name: str,
        game_id: str,
        idx: int,
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
        self.idx = idx
        self.role = role

        self.sent_talk_count: int = 0
        self.sent_whisper_count: int = 0
        self.llm_model: BaseChatModel | None = None
        self.llm_message_history: list[BaseMessage] = []

    def set_packet(self, packet: Packet) -> None:
        """パケット情報をセットする."""
        self.request = packet.request
        if packet.info is not None:
            self.info = packet.info
        if packet.setting is not None:
            self.setting = packet.setting
        if packet.talk_history is not None:
            self.talk_history.extend(packet.talk_history)
        if packet.whisper_history is not None:
            self.whisper_history.extend(packet.whisper_history)
        if self.request == Request.INITIALIZE:
            self.talk_history: list[Talk] = []
            self.whisper_history: list[Talk] = []
            self.llm_message_history: list[BaseMessage] = []
        self.agent_logger.logger.debug(packet)

    def get_alive_agents(self) -> list[str]:
        """生存しているエージェントのリストを取得する."""
        if self.info is None:
            return []
        if self.info.status_map is None:
            return []
        return [k for k, v in self.info.status_map.items() if v == Status.ALIVE]

    def _send_message_to_llm(self, content: str) -> str | None:
        if self.llm_model is None:
            self.agent_logger.logger.error("LLM is not initialized")
            return None
        try:
            self.llm_message_history.append(HumanMessage(content=content))
            response = self.llm_model.invoke(self.llm_message_history)
            response_content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content[0])
            )
            self.llm_message_history.append(AIMessage(content=response_content))
            self.agent_logger.logger.info(["LLM", content, response_content])
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
                    api_key=SecretStr(str(self.config["openai"]["api_key"])),
                )
            case "google":
                self.llm_model = ChatGoogleGenerativeAI(
                    model=str(self.config["google"]["model"]),
                    temperature=float(self.config["google"]["temperature"]),
                    api_key=SecretStr(str(self.config["google"]["api_key"])),
                )
            case _:
                raise ValueError(model_type, "Unknown LLM type")

        prompt = f"""
        あなたは人狼ゲームのエージェントです。
        あなたの名前は{self.info.agent}です。
        あなたの役職は{self.role}です。

        これからゲームを進行していきます。リクエストが来た際には、適切な応答を返してください。

        トークリクエストと囁きリクエストに対しては、ゲーム内で発言するべき内容のみを出力してください。
        履歴がある場合は、それを参考にしてください。ない場合は、適切な内容を出力してください。
        これ以上の情報を得られないと考えたときなどトークを終了したい場合については「Over」と出力してください。

        他のリクエストに対しては、行動の対象となるエージェントの名前のみを出力してください。
        対象となる生存しているエージェントの一覧が付与されています。

        あなたのレスポンスはそのままゲーム内に送信されるため、不要な情報を含めないでください。
        """
        self._send_message_to_llm(prompt)

    def daily_initialize(self) -> None:
        """昼開始リクエストに対する処理を行う."""
        message = "昼開始リクエスト"
        if self.info is not None:
            message += f"{self.info.day}日目\n"
            if self.info.medium_result is not None:
                message += f"霊能結果: {self.info.medium_result}\n"
            if self.info.divine_result is not None:
                message += f"占い結果: {self.info.divine_result}\n"
            if self.info.executed_agent is not None:
                message += f"追放結果: {self.info.executed_agent}\n"
            if self.info.attacked_agent is not None:
                message += f"襲撃結果: {self.info.attacked_agent}\n"
            if self.info.vote_list is not None:
                message += f"投票結果: {self.info.vote_list}\n"
            if self.info.attack_vote_list is not None:
                message += f"襲撃投票結果: {self.info.attack_vote_list}\n"
        sleep(3)
        self._send_message_to_llm(message)

    @timeout
    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        message = f"""
        囁きリクエスト
        履歴:
        {"\n".join(
            [
                f"{w.agent}: {w.text}"
                for w in self.whisper_history[self.sent_whisper_count :]
            ]
        )}
        """
        sleep(3)
        self.sent_whisper_count = len(self.whisper_history)
        return self._send_message_to_llm(message) or ""

    @timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        message = f"""
        トークリクエスト
        履歴:
        {"\n".join(
            [
                f"{t.agent}: {t.text}"
                for t in self.talk_history[self.sent_talk_count :]
            ]
        )}
        """
        sleep(3)
        self.sent_talk_count = len(self.talk_history)
        return self._send_message_to_llm(message) or ""

    def daily_finish(self) -> None:
        """昼終了リクエストに対する処理を行う."""
        message = "昼終了リクエスト"
        if self.info is not None:
            message += f"{self.info.day}日目\n"
            if self.info.medium_result is not None:
                message += f"霊能結果: {self.info.medium_result}\n"
            if self.info.divine_result is not None:
                message += f"占い結果: {self.info.divine_result}\n"
            if self.info.executed_agent is not None:
                message += f"追放結果: {self.info.executed_agent}\n"
            if self.info.attacked_agent is not None:
                message += f"襲撃結果: {self.info.attacked_agent}\n"
            if self.info.vote_list is not None:
                message += f"投票結果: {self.info.vote_list}\n"
            if self.info.attack_vote_list is not None:
                message += f"襲撃投票結果: {self.info.attack_vote_list}\n"
        sleep(3)
        self._send_message_to_llm(message)

    @timeout
    def divine(self) -> str:
        """占いリクエストに対する応答を返す."""
        message = f"""
        占いリクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self._send_message_to_llm(message) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def guard(self) -> str:
        """護衛リクエストに対する応答を返す."""
        message = f"""
        護衛リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self._send_message_to_llm(message) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        message = f"""
        投票リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self._send_message_to_llm(message) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def attack(self) -> str:
        """襲撃リクエストに対する応答を返す."""
        message = f"""
        襲撃リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        sleep(3)
        return self._send_message_to_llm(message) or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    def finish(self) -> None:
        """ゲーム終了リクエストに対する処理を行う."""

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
