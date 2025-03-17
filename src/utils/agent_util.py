"""エージェントに関するユーティリティ関数を提供するモジュール."""

import re

from aiwolf_nlp_common.packet import Role

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


def agent_name_to_idx(name: str) -> int:
    """インデックス付き文字列のエージェント名をインデックスに変換する."""
    match = re.match(r"Agent\[(\d{2})\]", name)
    if match is None:
        raise ValueError(name, "Invalid agent name format")
    return int(match.group(1))


def agent_idx_to_agent(idx: int) -> str:
    """インデックスをインデックス付き文字列のエージェント名に変換する."""
    return f"Agent[{idx:0>2d}]"


def set_role(prev_agent: Agent, role: Role) -> Agent:
    """エージェントの役職に応じたエージェントを設定する."""
    if role not in ROLE_TO_AGENT_CLS:
        raise ValueError(prev_agent.role, "Unknown role")
    agent = ROLE_TO_AGENT_CLS[role]()
    agent.transfer_state(prev_agent=prev_agent)
    return agent
