from contextlib import contextmanager
from queue import Queue, Empty

from mcdreforged.api.all import *

from auto_command.mcdr.mcdr_service import Service


class InfoGetter:
    class QueryTask:
        def __init__(self):
            self.querying_amount = 0
            self.result_queue = Queue()

        def is_querying(self):
            return self.querying_amount > 0

        @contextmanager
        def with_querying(self):
            self.querying_amount += 1
            try:
                yield
            finally:
                self.querying_amount -= 1

    def __init__(self, svc: Service):
        self._svc = svc
        self._info = self.QueryTask()

    def if_condition(self, timeout: float, condition: str, unless: bool = False) -> bool:
        cmd_t = f'/execute {"unless" if unless else "if"} {condition} run say ACInfoTrue'
        cmd_f = f'/execute {"if" if unless else "unless"} {condition} run say ACInfoFalse'
        with self._info.with_querying():
            self._svc.exec_mc_cmd(cmd_t)
            self._svc.exec_mc_cmd(cmd_f)
            try:
                return self._info.result_queue.get(timeout=timeout)
            except Empty:
                return False

    def on_info(self, info: Info):
        if not info.is_user:
            if self._info.is_querying():
                if 'ACInfo' in info.content:
                    self._info.result_queue.put('ACInfoTrue' in info.content)

