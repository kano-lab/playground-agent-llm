"""占い師のエージェントクラスを定義するモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiwolf_nlp_common.packet import Role

from agent.agent import Agent
from utils.timeout import timeout

if TYPE_CHECKING:
    from configparser import ConfigParser


class Seer(Agent):
    """占い師のエージェントクラス."""

    def __init__(
        self,
        config: ConfigParser,
        name: str,
        game_id: str,
        idx: int,
        role: Role,  # noqa: ARG002
    ) -> None:
        """占い師のエージェントを初期化する."""
        super().__init__(config, name, game_id, idx, Role.SEER)

    @timeout
    def talk(self) -> str:
        """トークリクエストに対する応答を返す."""
        return super().talk()

    @timeout
    def divine(self) -> str:
        """占いリクエストに対する応答を返す."""
        return super().divine()

    @timeout
    def vote(self) -> str:
        """投票リクエストに対する応答を返す."""
        return super().vote()
