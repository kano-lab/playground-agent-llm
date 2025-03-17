"""人狼のエージェントクラスを定義するモジュール."""

from __future__ import annotations

from agent.agent import Agent


class Werewolf(Agent):
    """人狼のエージェントクラス."""

    def __init__(self) -> None:
        """人狼のエージェントを初期化する."""
        super().__init__()

    @Agent.timeout
    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        return super().whisper()

    @Agent.timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return super().talk()

    @Agent.timeout
    @Agent.send_agent_index
    def vote(self) -> int:
        """投票リクエストに対する応答を返す."""
        return super().vote()

    @Agent.timeout
    @Agent.send_agent_index
    def attack(self) -> int:
        """襲撃リクエストに対する応答を返す."""
        return super().attack()
