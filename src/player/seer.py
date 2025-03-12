from __future__ import annotations

import random

from player.agent import Agent
from utils import agent_util


class Seer(Agent):

    def __init__(self) -> None:
        super().__init__()

    @Agent.timeout
    def talk(self) -> str:
        comment = random.choice(self.comments)  # noqa: S311
        if self.agent_log is not None:
            self.agent_log.talk(comment=comment)
        return comment

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.vote(vote_target=target)
        return target

    @Agent.timeout
    @Agent.send_agent_index
    def divine(self) -> int:
        target: int = agent_util.agent_name_to_idx(
            name=random.choice(self.get_alive_agents()),  # noqa: S311
        )
        if self.agent_log is not None:
            self.agent_log.divine(divine_target=target)
        return target

    def initialize(self) -> None:
        pass

    def daily_initialize(self) -> None:
        pass

    def daily_finish(self) -> None:
        pass

    def finish(self) -> None:
        pass
