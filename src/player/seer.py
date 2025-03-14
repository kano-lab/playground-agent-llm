from __future__ import annotations

import random

from player.agent import Agent
from utils import agent_util


class Seer(Agent):

    def __init__(self) -> None:
        super().__init__()

    @Agent.timeout
    def talk(self) -> str:
        return random.choice(self.comments)  # noqa: S311

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        return target

    @Agent.timeout
    @Agent.send_agent_index
    def divine(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        return target

    def initialize(self) -> None:
        pass

    def daily_initialize(self) -> None:
        pass

    def daily_finish(self) -> None:
        pass

    def finish(self) -> None:
        pass
