from typing import Optional

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage, CommandStack
from auto_command.tools.ac_time import ACTime
from auto_command.exceptions import ACTimeFormatMismatchException
from auto_command.task.interval_send_task import IntervalSendTask


class EditCommandStackInfoTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage, interval_send_task: IntervalSendTask):
        self._cfg = ctx.cfg
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._storage = storage
        self._interval_send_task = interval_send_task

    def make_command_stack(self, source: CommandSource, name: str, perm: int, time: str = '0', desc: str = ''):
        try:
            self._utils.req_perm(source, perm)

            if not ACTime.is_time_format(time):
                desc = time + ' ' + desc
                time = '0'

            stack = CommandStack(
                perm=perm,
                interval=time,
                desc=desc
            )
            self._storage.add_stack(name, stack)

            # run timed cmd stack
            if ACTime.not_zero(time):
                self._interval_send_task.start_timed_stack(name)

        except Exception as e:
            self._svc.print(source, self._svc.tr('make_command_stack.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to add command stack {}'.format(name))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('make_command_stack.success', name), name))

    def del_command_stack(self, source: CommandSource, name: str):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            # stop timed cmd stack
            self._interval_send_task.stop_timed_stack(name)

            self._storage.pop_stack(name)
        except Exception as e:
            self._svc.print(source, self._svc.tr('del_command_stack.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to delete command stack {}'.format(name))
        else:
            self._svc.print(source, self._svc.tr('del_command_stack.success', name))

    def stack_change_name(self, source: CommandSource, name: str, new_name: str):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)
            self._storage.change_name(name, new_name)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_change_name.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to change name of stack {}'.format(name))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_change_name.success', name, new_name), new_name))

    def stack_change_perm(self, source: CommandSource, name: str, level: int):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, max(level, stack.perm))
            self._storage.change_perm(name, level)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_change_perm.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to change permission of stack {}'.format(name))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_change_perm.success', name), name))

    def stack_change_interval(self, source: CommandSource, name: str, time: str):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            if not ACTime.is_time_format(time):
                raise ACTimeFormatMismatchException(time)

            self._storage.change_interval(name, time)

            # run or stop timed cmd stack
            if ACTime.is_zero(time):
                self._interval_send_task.stop_timed_stack(name)
            else:
                self._interval_send_task.start_timed_stack(name)

        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_change_interval.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to change time interval of stack {}'.format(name))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_change_interval.success', name), name))

    def stack_change_desc(self, source: CommandSource, name: str, desc: str):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)
            self._storage.change_desc(name, desc)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_change_desc.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to change description of stack {}'.format(name))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_change_desc.success', name), name))
