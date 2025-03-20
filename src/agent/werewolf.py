"""人狼のエージェントクラスを定義するモジュール."""

from __future__ import annotations

from aiwolf_nlp_common.packet import Role

from agent.agent import Agent
from utils.timeout import timeout


class Werewolf(Agent):
    """人狼のエージェントクラス."""

    def __init__(
        self,
        config: dict,
        name: str,
        game_id: str,
        idx: int,
        role: Role,  # noqa: ARG002
    ) -> None:
        """人狼のエージェントを初期化する."""
        super().__init__(config, name, game_id, idx, Role.WEREWOLF)

    @timeout
    def whisper(self) -> str:
        """囁きリクエストに対する応答を返す."""
        return super().whisper()

    @timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return super().talk()

    @timeout
    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        return super().vote()

    @timeout
    def attack(self) -> str:
        """襲撃リクエストに対する応答を返す."""
        return super().attack()
