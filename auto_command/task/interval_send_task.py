from typing import Callable
from threading import RLock

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage
from auto_command.tools.timer import FlexibleAsyncTimer
from auto_command.constant import DEFAULT_TIME_INTERVAL_UNIT
from auto_command.tools.ac_time import ACTime
from auto_command.exceptions import ACTimeFormatMismatchException, ACZeroTimeIntervalException


class IntervalSendTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage, send_command_stack: Callable[[CommandSource, str], None]):
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._source = self._svc.get_plugin_command_source()
        self._time = ctx.time
        self._storage = storage
        self._send_command_stack = send_command_stack
        self._timers: [str, FlexibleAsyncTimer] = {}
        self.__lock = RLock()

    def reset_timed_stacks(self):
        with self.__lock:
            for name in self._storage.timed_stack_names():
                self.start_timed_stack(name)

    def stop_timed_stacks(self):
        with self.__lock:
            for name in self._storage.timed_stack_names():
                self.stop_timed_stack(name)

    @new_thread
    def start_timed_stack(self, name):
        try:
            with self.__lock:
                stack = self._storage.get(name)

                timer: FlexibleAsyncTimer
                reset: bool = False
                if name in self._timers:
                    timer = self._timers[name]
                    reset = True
                else:
                    timer = FlexibleAsyncTimer(lambda: self._send_command_stack(self._svc.get_plugin_command_source(), name))
                    self._timers[name] = timer

                if not ACTime.is_time_format(stack.interval):
                    raise ACTimeFormatMismatchException(stack.interval)
                if ACTime.is_zero(stack.interval):
                    raise ACZeroTimeIntervalException

                async def _inline():
                    await self._time.sleep(stack.interval, DEFAULT_TIME_INTERVAL_UNIT)

                timer.start(_inline)

        except Exception as e:
            self._svc.print(self._source, self._svc.tr('start_timer.fail', name, self._utils.get_exception_msg(e)), tell=False)
            self._svc.log_exception('Failed to start timer of {}'.format(name))
        else:
            msg: RTextBase
            if reset:
                msg = self._svc.tr('start_timer.reset', name)
            else:
                msg = self._svc.tr('start_timer.start', name)
            self._svc.print(self._source, self._utils.click_info(msg, name), tell=False)

    def stop_timed_stack(self, name):
        try:
            with self.__lock:
                stop: bool = False
                if name in self._timers:
                    stop = True
                    timer: FlexibleAsyncTimer = self._timers[name]
                    timer.stop()
                    self._timers.pop(name)

        except Exception as e:
            self._svc.print(self._source, self._svc.tr('stop_timer.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to stop timer of {}'.format(name))
        else:
            if stop:
                self._svc.print(self._source, self._utils.click_info(self._svc.tr('stop_timer.success', name), name), tell=False)
