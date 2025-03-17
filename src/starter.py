"""エージェントを起動するためのモジュール."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import utils.agent_util
from agent.agent import Agent
from utils.agent_logger import AgentLogger

if TYPE_CHECKING:
    from configparser import ConfigParser

from time import sleep

from aiwolf_nlp_common.client import Client
from aiwolf_nlp_common.packet import Request


def connect(idx: int, config: ConfigParser) -> None:  # noqa: C901
    """エージェントを起動する."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    while True:
        client = Client(
            url=config.get("websocket", "url"),
            token=(
                config.get("websocket", "token")
                if config.has_option("websocket", "token")
                else None
            ),
        )
        name = config.get("agent", "team") + str(idx)
        while True:
            try:
                client.connect()
                logger.info("エージェント %s がゲームサーバに接続しました", name)
                break
            except Exception as ex:  # noqa: BLE001
                logger.warning(
                    "エージェント %s がゲームサーバに接続できませんでした",
                    name,
                )
                logger.warning(ex)
                logger.info("再接続を試みます")
                sleep(15)

        agent = Agent(config=config, name=name)
        agent_logger = AgentLogger(config=config, name=name)
        while True:
            packet = client.receive()
            agent_logger.logger.debug(packet)
            if packet.request == Request.INITIALIZE:
                if packet.info is None:
                    raise ValueError(packet.info, "Info not found")
                agent_logger.set_game_id(game_id=packet.info.game_id)
                if packet.info.agent is None or packet.info.role_map is None:
                    raise ValueError(packet.info, "Agent or role_map not found")
                role = packet.info.role_map.get(packet.info.agent)
                if role is None:
                    raise ValueError(packet.info, "Role not found")
                agent = utils.agent_util.set_role(prev_agent=agent, role=role)
            agent.set_packet(packet)
            req = agent.action()
            if agent.request is not None:
                agent_logger.packet(agent.request, req)
                if req is not None:
                    client.send(req)
            if packet.request == Request.FINISH:
                break

        client.close()
        logger.info("エージェント %s とゲームサーバの接続を切断しました", name)
        if not config.getboolean("websocket", "auto_reconnect"):
            break
