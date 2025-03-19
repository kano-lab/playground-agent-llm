"""設定に応じたエージェントを起動するスクリプト."""

import logging
import multiprocessing
from configparser import ConfigParser
from pathlib import Path

import starter

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    multiprocessing.set_start_method("spawn")

    config_path = "./config/config.ini"
    if Path(config_path).exists():
        config = ConfigParser()
        config.read(config_path)
        logger.info("設定ファイルを読み込みました")
    else:
        raise FileNotFoundError(config_path, "設定ファイルが見つかりません")

    agent_num = int(config.get("agent", "num"))
    logger.info("エージェント数: %d", agent_num)
    if agent_num == 1:
        starter.connect(config)
    else:
        threads = []
        for i in range(agent_num):
            thread = multiprocessing.Process(
                target=starter.connect,
                args=(config, i + 1),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
