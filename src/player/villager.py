from __future__ import annotations

from player.agent import Agent


class Villager(Agent):

    def __init__(self) -> None:
        super().__init__()

    @Agent.timeout
    def talk(self) -> str:
        return super().talk()

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        return super().vote()

    def initialize(self) -> None:
        pass

    def daily_initialize(self) -> None:
        pass

    def daily_finish(self) -> None:
        pass

    def finish(self) -> None:
        pass
