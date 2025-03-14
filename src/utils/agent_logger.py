from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import configparser

    from aiwolf_nlp_common.packet import Request


class AgentLogger:
    def __init__(
        self,
        config: configparser.ConfigParser,
        name: str,
    ) -> None:
        self.config = config
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def set_game_id(self, game_id: str) -> None:
        if self.config.getboolean("log", "write"):
            file_handler = logging.FileHandler(
                Path(self.config.get("log", "output_dir"))
                / f"{game_id}_{self.name}.log",
                mode="w",
                encoding="utf-8",
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, req: Request, res: str | None) -> None:
        if not self.config.has_option("log", req.lower()):
            return
        if not self.config.getboolean("log", req.lower()):
            return
        if res is None:
            self.logger.info([str(req)])
        else:
            self.logger.info([str(req), res])
