"""占い師のエージェントクラスを定義するモジュール."""

from __future__ import annotations

from agent.agent import Agent


class Seer(Agent):
    """占い師のエージェントクラス."""

    def __init__(self) -> None:
        """占い師のエージェントを初期化する."""
        super().__init__()

    @Agent.timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return super().talk()

    @Agent.timeout
    @Agent.send_agent_index
    def divine(self) -> int:
        """占いリクエストに対する応答を返す."""
        return super().divine()

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        """投票リクエストに対する応答を返す."""
        return super().vote()
