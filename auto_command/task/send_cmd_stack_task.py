import asyncio

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage
from auto_command.tools.sender import CommandStackSender
from auto_command.task.interval_send_task import IntervalSendTask
from auto_command.tools.ac_time import ACTime


class SendCommandStackTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage, interval_send_task: IntervalSendTask):
        self._ctx = ctx
        self._storage = storage
        self._interval_send_task = interval_send_task

    def send_command_stack(self, source: CommandSource, name: str, condition='', unless=False):
        sender = CommandStackSender(self._ctx, source, self._storage)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sender.send_command_stack(name, condition, unless))
        loop.close()

        if not isinstance(source, PluginCommandSource):
            stack = self._storage.get(name)
            if ACTime.not_zero(stack.interval):
                self._interval_send_task.start_timed_stack(name)

