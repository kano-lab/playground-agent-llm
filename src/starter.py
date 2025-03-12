from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from utils.agent_log import AgentLog

if TYPE_CHECKING:
    from configparser import ConfigParser

    from utils.log_info import LogInfo

from time import sleep

from aiwolf_nlp_common.client import Client
from aiwolf_nlp_common.packet import Request

import player
import utils

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def connect(
    idx: int,
    config: ConfigParser,
    log_info: LogInfo,
) -> None:
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

    agent = player.agent.Agent(
        config=config,
        team_name=name,
        agent_log=AgentLog(config=config, agent_name=name, log_info=log_info),
    )
    while agent.request != Request.FINISH:
        packet = client.receive()
        agent.set_packet(packet)
        req = agent.action()
        if agent.request == Request.INITIALIZE:
            agent = utils.agent_util.set_role(prev_agent=agent)
        if req is not None:
            client.send(req)

    client.close()
    logger.info("エージェント %s とゲームサーバの接続を切断しました", name)


def execute(
    idx: int,
    config: ConfigParser,
    log_info: LogInfo,
) -> None:
    while True:
        connect(idx=idx, config=config, log_info=log_info)
        if not config.getboolean("websocket", "auto_reconnect"):
            break
