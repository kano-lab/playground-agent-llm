"""エージェント関連のユーティリティ関数を提供するモジュール."""

from configparser import ConfigParser

from aiwolf_nlp_common.packet import Packet, Role

from agent.agent import Agent
from agent.bodyguard import Bodyguard
from agent.medium import Medium
from agent.possessed import Possessed
from agent.seer import Seer
from agent.villager import Villager
from agent.werewolf import Werewolf
from utils.agent_utils import agent_name_to_idx

ROLE_TO_AGENT_CLS: dict[Role, type[Agent]] = {
    Role.WEREWOLF: Werewolf,
    Role.POSSESSED: Possessed,
    Role.SEER: Seer,
    Role.BODYGUARD: Bodyguard,
    Role.VILLAGER: Villager,
    Role.MEDIUM: Medium,
}


@staticmethod
def init_agent_from_packet(
    config: ConfigParser,
    name: str,
    packet: Packet,
) -> Agent:
    """役職に対応するエージェントクラスを初期化する."""
    if packet.info is None:
        raise ValueError(packet.info, "Info not found")
    if packet.info.agent is None or packet.info.role_map is None:
        raise ValueError(packet.info, "Agent or role_map not found")
    role = packet.info.role_map.get(packet.info.agent)
    if role is None:
        raise ValueError(packet.info, "Role not found")
    if packet.info.agent is None or packet.info.role_map is None:
        raise ValueError(packet.info, "Agent or role_map not found")
    idx = agent_name_to_idx(name=packet.info.agent)
    return ROLE_TO_AGENT_CLS[role](
        config=config,
        name=name,
        game_id=packet.info.game_id,
        idx=idx,
        role=role,
    )
