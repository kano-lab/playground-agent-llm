"""エージェントのログを出力するクラスを定義するモジュール."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiwolf_nlp_common.packet import Request


class AgentLogger:
    """エージェントのログを出力するクラス."""

    def __init__(
        self,
        config: dict,
        name: str,
        game_id: str,
    ) -> None:
        """エージェントのログを初期化する."""
        self.config = config
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(
            logging.getLevelNamesMapping()[str(self.config["log"]["level"]).upper()],
        )
        if bool(self.config["log"]["console_output"]):
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        if bool(self.config["log"]["file_output"]):
            output_dir = Path(str(self.config["log"]["output_dir"])) / game_id
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

    def packet(self, req: Request | None, res: str | None) -> None:
        """パケットのログを出力."""
        if req is None:
            return
        if req.lower() not in self.config["log"]["request"]:
            return
        if not bool(self.config["log"]["request"][req.lower()]):
            return
        if res is None:
            self.logger.info([str(req)])
        else:
            self.logger.info([str(req), res])
