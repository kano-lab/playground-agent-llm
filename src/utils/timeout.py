"""アクションタイムアウトを定義するモジュール."""

from collections.abc import Callable
from threading import Thread

from agent.agent import Agent


@staticmethod
def timeout(func: Callable) -> Callable:
    """アクションタイムアウトを設定するデコレータ."""

    def _wrapper(self: Agent, *args, **kwargs) -> str:  # noqa: ANN002, ANN003
        res = ""

        def execute_with_timeout() -> None:
            nonlocal res
            try:
                res = func(self, *args, **kwargs)
            except Exception as e:  # noqa: BLE001
                res = e

        thread = Thread(target=execute_with_timeout, daemon=True)
        thread.start()

        timeout_value = self.setting.timeout.action if self.setting else 0
        if timeout_value > 0:
            thread.join(timeout=timeout_value)
        else:
            thread.join()

        if isinstance(res, Exception):
            raise res

        return res

    return _wrapper
