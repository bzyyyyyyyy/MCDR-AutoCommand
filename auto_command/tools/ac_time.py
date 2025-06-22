import re
from typing import Dict
import asyncio

from mcdreforged.api.all import *

from auto_command.tools.tick_data_getter import TickDataGetter
from auto_command.exceptions import ACTimeFormatMismatchException
from auto_command.constant import COMMAND_TIMEOUT
from auto_command.exceptions import ACGetGametickTimeoutException


class ACTime:
    _format: Dict[str, str] = {
        'tick': r"^(\d+)(?i:tick|t)",
        'second': r"^(\d+\.\d+|\.\d+|\d+)(?i:second|sec|s)",
        'minute': r"^(\d+\.\d+|\.\d+|\d+)(?i:minute|min|m)",
        'hour': r"^(\d+\.\d+|\.\d+|\d+)(?i:hour|hr|h)",
        'day': r"^(\d+\.\d+|\.\d+|\d+)(?i:day|d)",
        'week': r"^(\d+\.\d+|\.\d+|\d+)(?i:week|wk|w)",
    }

    def __init__(self, tick_data_getter: TickDataGetter):
        self._tick_data_getter = tick_data_getter
        self._tps_gettable: bool = tick_data_getter.tps_gettable

    @classmethod
    def is_time_format(cls, time: str) -> bool:
        if re.fullmatch(r'^(?:\d+\.\d+|\.\d+|\d+)$', time):
            return True
        for pattern in cls._format.values():
            if re.fullmatch(pattern, time):
                return True
        return False

    @staticmethod
    def to_time(time: str, postfix: str) -> str:
        if re.fullmatch(r'^(?:\d+\.\d+|\.\d+|\d+)$', time):
            time += postfix
        return time

    @staticmethod
    def get_number(time: str) -> float:
        if m := re.match(r'^(\d+\.\d+|\.\d+|\d+)', time):
            return float(m.group(1))

    @staticmethod
    def is_zero(time: str) -> bool:
        return ACTime.get_number(time) == 0

    @staticmethod
    def not_zero(time: str) -> bool:
        return ACTime.get_number(time) != 0

    async def sleep(self, time: str, default_post: str):
        time = self.to_time(time, default_post)
        if not self.is_time_format(time):
            raise ACTimeFormatMismatchException(time)

        n, sec = self._time_to_s(time)
        if sec:
            await asyncio.sleep(n)
        else:
            await self._sleep_tick(int(n))

    async def _get_gametick(self) -> int:
        gt: int = self._tick_data_getter.get_gametick(timeout=COMMAND_TIMEOUT)
        if gt is None:
            raise ACGetGametickTimeoutException
        return gt

    async def _tick_step(self):
        await self._get_gametick()

    async def _sleep_tick(self, t: int):
        if t <= 3:
            for _ in range(t):
                await self._tick_step()
            return

        tps: float = 20

        if self._tps_gettable:
            tps = self._tick_data_getter.get_tps(timeout=COMMAND_TIMEOUT)
            t -= 1

        start_gt: int = await self._get_gametick()
        t -= 1

        target_gt: int = start_gt + t
        wait_sec: float
        current_gt: int
        while True:
            wait_sec = (t - 1) / tps  # -1tick for the time of get gametick func
            # TODO tick freeze case

            await asyncio.sleep(wait_sec)

            current_gt = await self._get_gametick()  # -1tick

            if current_gt >= target_gt:
                return
            else:
                tps = (current_gt - start_gt) / wait_sec
                t = target_gt - current_gt
                start_gt = current_gt

    @classmethod
    def _time_to_s(cls, time: str) -> tuple[float, bool]:
        unit: str = ''
        n: float = 0
        for u in cls._format:
            match = re.fullmatch(cls._format[u], time)
            if match:
                unit = u
                n = float(match.group(1))
                break
        if unit == 'tick':
            return n, False
        elif unit == 'second':
            return n, True
        elif unit == 'minute':
            return n * 60, True
        elif unit == 'hour':
            return n * 60 * 60, True
        elif unit == 'day':
            return n * 60 * 60 * 24, True
        elif unit == 'week':
            return n * 60 * 60 * 24 * 7, True

