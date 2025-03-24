"""エージェント関連のユーティリティ関数を提供するモジュール."""

import re

from aiwolf_nlp_common.packet import Packet, Role

from agent.agent import Agent
from agent.bodyguard import Bodyguard
from agent.medium import Medium
from agent.possessed import Possessed
from agent.seer import Seer
from agent.villager import Villager
from agent.werewolf import Werewolf

ROLE_TO_AGENT_CLS: dict[Role, type[Agent]] = {
    Role.WEREWOLF: Werewolf,
    Role.POSSESSED: Possessed,
    Role.SEER: Seer,
    Role.BODYGUARD: Bodyguard,
    Role.VILLAGER: Villager,
    Role.MEDIUM: Medium,
}


@staticmethod
def agent_name_to_idx(name: str) -> int:
    """インデックス付き文字列のエージェント名をインデックスに変換する."""
    match = re.match(r"Agent\[(\d{2})\]", name)
    if not match:
        raise ValueError(name, "Invalid agent name format")
    return int(match.group(1))


@staticmethod
def agent_idx_to_agent(idx: int) -> str:
    """インデックスをインデックス付き文字列のエージェント名に変換する."""
    return f"Agent[{idx:0>2d}]"


@staticmethod
def init_agent_from_packet(
    config: dict,
    name: str,
    packet: Packet,
) -> Agent:
    """役職に対応するエージェントクラスを初期化する."""
    if not packet.info:
        raise ValueError(packet.info, "Info not found")
    role = packet.info.role_map.get(packet.info.agent)
    if not role:
        raise ValueError(packet.info, "Role not found")
    idx = agent_name_to_idx(name=packet.info.agent)
    return ROLE_TO_AGENT_CLS[role](
        config=config,
        name=name,
        game_id=packet.info.game_id,
        idx=idx,
        role=role,
    )
