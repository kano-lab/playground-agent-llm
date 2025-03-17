"""霊媒師のエージェントクラスを定義するモジュール."""

from __future__ import annotations

from agent.agent import Agent


class Medium(Agent):
    """霊媒師のエージェントクラス."""

    def __init__(self) -> None:
        """霊媒師のエージェントを初期化する."""
        super().__init__()

    @Agent.timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return super().talk()

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        """投票リクエストに対する応答を返す."""
        return super().vote()
