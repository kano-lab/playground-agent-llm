"""エージェント関連のユーティリティ関数を提供するモジュール."""

import re


@staticmethod
def agent_name_to_idx(name: str) -> int:
    """インデックス付き文字列のエージェント名をインデックスに変換する."""
    match = re.match(r"Agent\[(\d{2})\]", name)
    if match is None:
        raise ValueError(name, "Invalid agent name format")
    return int(match.group(1))


@staticmethod
def agent_idx_to_agent(idx: int) -> str:
    """インデックスをインデックス付き文字列のエージェント名に変換する."""
    return f"Agent[{idx:0>2d}]"
