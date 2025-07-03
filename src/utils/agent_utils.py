"""エージェント関連のユーティリティ関数を提供するモジュール."""

from typing import Any

from aiwolf_nlp_common.packet import Packet

from agent.agent import Agent


@staticmethod
def init_agent_from_packet(
    config: dict[str, Any],
    name: str,
    packet: Packet,
) -> Agent:
    """役職に対応するエージェントクラスを初期化する."""
    if not packet.info:
        raise ValueError(packet.info, "Info not found")
    role = packet.info.role_map.get(packet.info.agent)
    if not role:
        raise ValueError(packet.info, "Role not found")
    return Agent(
        config=config,
        name=name,
        game_id=packet.info.game_id,
        role=role,
    )
