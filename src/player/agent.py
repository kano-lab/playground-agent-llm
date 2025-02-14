from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from utils import agent_util

if TYPE_CHECKING:
    import configparser

    from utils.agent_log import AgentLog

import random
from threading import Thread
from typing import Callable

from aiwolf_nlp_common.packet import Info, Packet, Request, Role, Setting, Status, Talk


class Agent:

    def __init__(
        self,
        config: configparser.ConfigParser | None = None,
        team_name: str | None = None,
        agent_log: AgentLog | None = None,
    ) -> None:
        self.role: Role | None = None
        self.team_name: str = team_name if team_name is not None else ""
        self.idx: int = -1

        self.request: Request | None = None
        self.info: Info | None = None
        self.setting: Setting | None = None
        self.talk_history: list[Talk] = []
        self.whisper_history: list[Talk] = []

        self.agent_log = agent_log

        self.comments: list[str] = []
        if config is not None:
            with Path.open(
                Path(config.get("path", "random_talk")),
                encoding="utf-8",
            ) as f:
                self.comments = f.read().splitlines()

    @staticmethod
    def timeout(func: Callable) -> Callable:
        def _wrapper(self, *args, **kwargs) -> str:  # noqa: ANN001, ANN002, ANN003
            res = ""

            def execute_with_timeout() -> None:
                nonlocal res
                try:
                    res = func(self, *args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    res = e

            thread = Thread(target=execute_with_timeout, daemon=True)
            thread.start()
            if self.action_timeout > 0:
                thread.join(timeout=self.action_timeout)
            else:
                thread.join()

            if isinstance(res, Exception):
                raise res

            return res

        return _wrapper

    @staticmethod
    def send_agent_index(func: Callable) -> Callable:
        def _wrapper(self, *args, **kwargs) -> str:  # noqa: ANN001, ANN002, ANN003
            res = func(self, *args, **kwargs)
            if type(res) is not int:
                return res
            return agent_util.agent_idx_to_agent(idx=res)

        return _wrapper

    def set_packet(self, packet: Packet) -> None:
        if packet is None:
            return
        self.request = packet.request
        if self.info is not None and packet.info is not None:
            self.info = packet.info
        if self.setting is not None and packet.setting is not None:
            self.setting = packet.setting
        if packet.talk_history is not None:
            self.talk_history.extend(packet.talk_history)
        if packet.whisper_history is not None:
            self.whisper_history.extend(packet.whisper_history)

        if self.request == Request.INITIALIZE:
            if self.info is None:
                return
            if self.info.agent is None or self.info.role_map is None:
                return
            self.idx = agent_util.agent_name_to_idx(name=self.info.agent)
            self.role = self.info.role_map.get(self.info.agent)

    def get_alive_agents(self) -> list[str]:
        if self.info is None:
            return []
        if self.info.status_map is None:
            return []
        return [k for k, v in self.info.status_map.items() if v == Status.ALIVE]

    @timeout
    def name(self) -> str:
        return self.team_name

    @timeout
    def talk(self) -> str:
        comment = random.choice(self.comments)  # noqa: S311
        if self.agent_log is not None:
            self.agent_log.talk(comment=comment)
        return comment

    @timeout
    def whisper(self) -> str:
        comment = random.choice(self.comments)  # noqa: S311
        if self.agent_log is not None:
            # :TODO implement whisper log
            self.agent_log.talk(comment=comment)
        return comment

    @timeout
    @send_agent_index
    def vote(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.vote(vote_target=target)
        return target

    @timeout
    @send_agent_index
    def divine(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.divine(divine_target=target)
        return target

    @timeout
    @send_agent_index
    def guard(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.divine(guard_target=target)
            # :TODO implement guard log
        return target

    @timeout
    @send_agent_index
    def attack(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.attack(attack_target=target)
        return target

    def initialize(self) -> None:
        pass

    def daily_initialize(self) -> None:
        pass

    def daily_finish(self) -> None:
        pass

    def finish(self) -> None:
        pass

    def action(self) -> str | None:  # noqa: C901, PLR0911
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
                return self.name()
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
                if self.agent_log is not None and self.agent_log.is_write:
                    self.agent_log.close()
        return None

    def transfer_state(self, prev_agent: Agent) -> None:
        self.role = prev_agent.role
        self.team_name = prev_agent.team_name
        self.idx = prev_agent.idx

        self.request = prev_agent.request
        self.info = prev_agent.info
        self.setting = prev_agent.setting
        self.talk_history = prev_agent.talk_history
        self.whisper_history = prev_agent.whisper_history

        self.agent_log = prev_agent.agent_log

        self.comments = prev_agent.comments
