import re

from aiwolf_nlp_common.packet import Role

from player.agent import Agent
from player.possessed import Possessed
from player.seer import Seer
from player.villager import Villager
from player.werewolf import Werewolf


def set_role(
    prev_agent: Agent,
) -> Agent:
    role: Role | None = None
    if (
        prev_agent.info is not None
        and prev_agent.info.agent is not None
        and prev_agent.info.role_map is not None
    ):
        role = prev_agent.info.role_map.get(prev_agent.info.agent)
    agent: Agent
    match role:
        case Role.VILLAGER:
            agent = Villager()
        case Role.WEREWOLF:
            agent = Werewolf()
        case Role.SEER:
            agent = Seer()
        case Role.POSSESSED:
            agent = Possessed()
        case _:
            raise ValueError(prev_agent.role, "Unknown role")
    agent.transfer_state(prev_agent=prev_agent)
    return agent


def agent_name_to_idx(name: str) -> int:
    match = re.search(r"\d+", name)
    if match is None:
        raise ValueError(name, "No number found in agent name")
    return int(match.group())


def agent_idx_to_agent(idx: int) -> str:
    return f"Agent[{idx:0>2d}]"
