"""エージェントの基底クラスを定義するモジュール."""

from __future__ import annotations

import random
from pathlib import Path

from aiwolf_nlp_common.packet import Info, Packet, Request, Role, Setting, Status, Talk

from utils.agent_logger import AgentLogger
from utils.timeout import timeout


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

        self.comments: list[str] = []
        if self.config is not None:
            with Path.open(
                Path(str(self.config["path"]["random_talk"])),
                encoding="utf-8",
            ) as f:
                self.comments = f.read().splitlines()

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

    def daily_initialize(self) -> None:
        """昼開始リクエストに対する処理を行う."""

    @timeout
    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        return random.choice(self.comments)  # noqa: S311

    @timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return random.choice(self.comments)  # noqa: S311

    def daily_finish(self) -> None:
        """昼終了リクエストに対する処理を行う."""

    @timeout
    def divine(self) -> str:
        """占いリクエストに対する応答を返す."""
        return random.choice(self.get_alive_agents())  # noqa: S311

    @timeout
    def guard(self) -> str:
        """護衛リクエストに対する応答を返す."""
        return random.choice(self.get_alive_agents())  # noqa: S311

    @timeout
    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        return random.choice(self.get_alive_agents())  # noqa: S311

    @timeout
    def attack(self) -> str:
        """襲撃リクエストに対する応答を返す."""
        return random.choice(self.get_alive_agents())  # noqa: S311

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
