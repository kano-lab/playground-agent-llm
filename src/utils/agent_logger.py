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
        self.logger.setLevel(
            logging.getLevelNamesMapping()[self.config.get("log", "level").upper()],
        )
        if self.config.getboolean("log", "console_output"):
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_game_id(self, game_id: str) -> None:
        if self.config.getboolean("log", "file_output"):
            output_dir = Path(self.config.get("log", "output_dir")) / game_id
            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            handler = logging.FileHandler(
                output_dir / f"{self.name}.log",
                mode="w",
                encoding="utf-8",
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def packet(self, req: Request, res: str | None) -> None:
        if not self.config.has_option("log", req.lower()):
            return
        if not self.config.getboolean("log", req.lower()):
            return
        if res is None:
            self.logger.info([str(req)])
        else:
            self.logger.info([str(req), res])
