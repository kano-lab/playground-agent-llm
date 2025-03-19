"""エージェントの基底クラスを定義するモジュール."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from utils.timeout import timeout

if TYPE_CHECKING:
    from configparser import ConfigParser

    from google.genai import Client
    from google.genai.chats import Chat

import random

from aiwolf_nlp_common.packet import Info, Packet, Request, Role, Setting, Status, Talk
from google import genai

from utils.agent_logger import AgentLogger


class Agent:
    """エージェントの基底クラス."""

    def __init__(
        self,
        config: ConfigParser,
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

        self.client: Client | None = None
        self.chat: Chat | None
        self.sent_talk_count: int = 0
        self.sent_whisper_count: int = 0

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
        self.agent_logger.logger.debug(packet)

    def get_alive_agents(self) -> list[str]:
        """生存しているエージェントのリストを取得する."""
        if self.info is None:
            return []
        if self.info.status_map is None:
            return []
        return [k for k, v in self.info.status_map.items() if v == Status.ALIVE]

    @timeout
    def name(self) -> str:
        """名前リクエストに対する応答を返す."""
        return self.agent_name

    def initialize(self) -> None:
        """ゲーム開始リクエストに対する初期化処理を行う."""
        if self.config is None or self.info is None:
            return
        self.client = genai.Client(api_key=self.config.get("gemini", "api_key"))
        self.chat = self.client.chats.create(model=self.config.get("gemini", "model"))
        self.chat.send_message(
            f"""
            あなたは人狼ゲームのエージェントです。
            あなたの名前は{self.info.agent}です。
            あなたの役職は{self.role}です。

            これからゲームを進行していきます。リクエストが来た際には、適切な応答を返してください。
            トークリクエストと囁きリクエストに対しては、ゲーム内で発言するべき内容のみを出力してください。
            他のリクエストに対しては、行動の対象となるエージェントの名前のみを出力してください。

            説明は以上です。「はい」と出力してください。
            """,
        )

    def daily_initialize(self) -> None:
        """昼開始リクエストに対する処理を行う."""

    @timeout
    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        if self.chat is None:
            return ""
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
        return (self.chat.send_message(message).text or "").strip()

    @timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        if self.chat is None:
            return ""
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
        return (self.chat.send_message(message).text or "").strip()

    def daily_finish(self) -> None:
        """昼終了リクエストに対する処理を行う."""

    @timeout
    def divine(self) -> str:
        """占いリクエストに対する応答を返す."""
        if self.chat is None:
            return random.choice(self.get_alive_agents())  # noqa: S311
        message = f"""
        占いリクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self.chat.send_message(message).text or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def guard(self) -> str:
        """護衛リクエストに対する応答を返す."""
        if self.chat is None:
            return random.choice(self.get_alive_agents())  # noqa: S311
        message = f"""
        護衛リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self.chat.send_message(message).text or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        if self.chat is None:
            return random.choice(self.get_alive_agents())  # noqa: S311
        message = f"""
        投票リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self.chat.send_message(message).text or random.choice(  # noqa: S311
            self.get_alive_agents(),
        )

    @timeout
    def attack(self) -> str:
        """襲撃リクエストに対する応答を返す."""
        if self.chat is None:
            return random.choice(self.get_alive_agents())  # noqa: S311
        message = f"""
        襲撃リクエスト
        対象:
        {"\n".join(self.get_alive_agents())}
        """
        sleep(3)
        return self.chat.send_message(message).text or random.choice(  # noqa: S311
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
