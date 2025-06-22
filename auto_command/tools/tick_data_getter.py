from contextlib import contextmanager
from queue import Queue, Empty
from typing import Optional

from mcdreforged.api.all import *

from auto_command.mcdr.mcdr_service import Service
from auto_command.config import TickDataGetterConfig


class TickDataGetter:
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

    def __init__(self, svc: Service, cfg: TickDataGetterConfig):
        self._svc = svc
        self._cfg = cfg
        self._gametime = self.QueryTask()
        self._tps = self.QueryTask()
        self._tps_gettable: bool = False
        if cfg.tps_command != "":
            self._tps_gettable = True

    @property
    def tps_gettable(self) -> bool:
        return self._tps_gettable

    def get_gametick(self, timeout: float) -> Optional[int]:
        with self._gametime.with_querying():
            self._svc.exec_mc_cmd(self._cfg.gametime_command)
            try:
                return self._gametime.result_queue.get(timeout=timeout)
            except Empty:
                return None

    def get_tps(self, timeout: float) -> Optional[float]:
        with self._tps.with_querying():
            self._svc.exec_mc_cmd(self._cfg.tps_command)
            try:
                return self._tps.result_queue.get(timeout=timeout)
            except Empty:
                return None

    def on_info(self, info: Info):
        if not info.is_user:
            if self._gametime.is_querying():
                if (m := self._cfg.gametime_output_regex.match(info.content)) is not None:
                    gametime = int(m.group(1))
                    self._gametime.result_queue.put(gametime)
            if self._tps.is_querying():
                if (m := self._cfg.tps_output_regex.match(info.content)) is not None:
                    tps = float(m.group(1))
                    self._tps.result_queue.put(tps)

