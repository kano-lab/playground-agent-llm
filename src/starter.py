from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from utils.agent_logger import AgentLogger

if TYPE_CHECKING:
    from configparser import ConfigParser

from time import sleep

from aiwolf_nlp_common.client import Client
from aiwolf_nlp_common.packet import Request

import player
import utils


def connect(idx: int, config: ConfigParser) -> None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    client: Client = Client(
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
            logger.warning("エージェント %s がゲームサーバに接続できませんでした", name)
            logger.warning(ex)
            logger.info("再接続を試みます")
            sleep(15)

    agent = player.agent.Agent(config=config, name=name)
    agent_logger = AgentLogger(config=config, name=name)
    while agent.request != Request.FINISH:
        packet = client.receive()
        agent_logger.logger.debug(packet)
        agent.set_packet(packet)
        req = agent.action()
        if agent.request == Request.INITIALIZE:
            agent = utils.agent_util.set_role(prev_agent=agent)
            if agent.info is not None:
                agent_logger.set_game_id(game_id=agent.info.game_id)
        if agent.request is not None:
            agent_logger.packet(agent.request, req)
            if req is not None:
                client.send(req)

    client.close()
    logger.info("エージェント %s とゲームサーバの接続を切断しました", name)


def execute(idx: int, config: ConfigParser) -> None:
    while True:
        connect(idx=idx, config=config)
        if not config.getboolean("websocket", "auto_reconnect"):
            break
