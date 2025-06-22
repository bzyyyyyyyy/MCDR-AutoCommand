from typing import Optional

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage
from auto_command.task.help_msg_task import HelpMessageTask
from auto_command.task.list_cmd_stack_task import ListCommandStackTask
from auto_command.task.edit_cmd_stack_info_task import EditCommandStackInfoTask
from auto_command.task.info_cmd_stack_task import InfoCommandStackTask
from auto_command.task.edit_cmd_in_stack_task import EditCommandInStackTask
from auto_command.task.send_cmd_stack_task import SendCommandStackTask
from auto_command.task.interval_send_task import IntervalSendTask
from auto_command.task.cmd_perm_task import CommandPermTask
from auto_command.task.record_cmd_stack_task import RecordCommandStackTask


class TaskManager:
    def __init__(self, ctx: Context, cmd_stack_storage: CommandStackStorage):
        self._svc = ctx.svc
        self._cfg = ctx.cfg
        self._help_msg_task = HelpMessageTask(ctx)
        self._list_cmd_stack_task = ListCommandStackTask(ctx, cmd_stack_storage)
        self._interval_send_task = IntervalSendTask(ctx, cmd_stack_storage, self.send_command_stack)
        self._send_cmd_stack_task = SendCommandStackTask(ctx, cmd_stack_storage, self._interval_send_task)
        self._edit_cmd_stack_info_task = EditCommandStackInfoTask(ctx, cmd_stack_storage, self._interval_send_task)
        self._info_cmd_stack_task = InfoCommandStackTask(ctx, cmd_stack_storage)
        self._cmd_perm_task = CommandPermTask(ctx, cmd_stack_storage)
        self._edit_cmd_in_stack_task = EditCommandInStackTask(ctx, cmd_stack_storage, self._cmd_perm_task)
        self._record_cmd_stack_task = RecordCommandStackTask(ctx, cmd_stack_storage, self._edit_cmd_in_stack_task, self._cmd_perm_task)

    @new_thread
    def print_simple_help_message(self, source: CommandSource):
        self._help_msg_task.print_simple_help_message(source)

    @new_thread
    def print_full_help_message(self, source: CommandSource):
        self._help_msg_task.print_full_help_message(source)

    @new_thread
    def list_command_stack(self, source: CommandSource, *, keyword: Optional[str] = None, page: Optional[int] = None):
        self._list_cmd_stack_task.list_command_stack(source, keyword, page)

    @new_thread
    def send_command_stack(self, source: CommandSource, name: str, condition='', unless=False):
        self._send_cmd_stack_task.send_command_stack(source, name, condition, unless)

    @new_thread
    def make_command_stack(self, source: CommandSource, name: str, perm: int, time: str = '0', desc: str = ''):
        self._edit_cmd_stack_info_task.make_command_stack(source, name, perm, time, desc)

    @new_thread
    def del_command_stack(self, source: CommandSource, name: str):
        self._edit_cmd_stack_info_task.del_command_stack(source, name)

    @new_thread
    def info_command_stack(self, source: CommandSource, name: str):
        self._info_cmd_stack_task.info_command_stack(source, name)

    @new_thread
    def stack_add_command(self, source: CommandSource, name: str, command: str, line: int = 0):
        self._edit_cmd_in_stack_task.stack_add_command(source, name, command, line)

    @new_thread
    def stack_edit_command(self, source: CommandSource, name: str, command: str, line: int):
        self._edit_cmd_in_stack_task.stack_edit_command(source, name, command, line)

    @new_thread
    def stack_del_command(self, source: CommandSource, name: str, line: Optional[int] = None):
        self._edit_cmd_in_stack_task.stack_del_command(source, name, line)

    @new_thread
    def stack_change_name(self, source: CommandSource, name: str, new_name: str):
        self._edit_cmd_stack_info_task.stack_change_name(source, name, new_name)

    @new_thread
    def stack_change_perm(self, source: CommandSource, name: str, level: int):
        self._edit_cmd_stack_info_task.stack_change_perm(source, name, level)

    @new_thread
    def stack_change_interval(self, source: CommandSource, name: str, time: str):
        self._edit_cmd_stack_info_task.stack_change_interval(source, name, time)

    @new_thread
    def stack_change_desc(self, source: CommandSource, name: str, desc: str):
        self._edit_cmd_stack_info_task.stack_change_desc(source, name, desc)

    @new_thread
    def stack_record(self, source: CommandSource, name: str):
        self._record_cmd_stack_task.stack_record(source, name)

    @new_thread
    def print_wait_help(self, source: CommandSource, time: str):
        self._help_msg_task.print_wait_help(source, time)

    @new_thread
    def print_perm_help(self, source: CommandSource, regex: str, white: bool = True):
        self._help_msg_task.print_perm_help(source, regex, white)

    @new_thread
    def on_user_info(self, info: Info):
        self._record_cmd_stack_task.on_user_info(info)

    @new_thread('const_default_stacks')
    def const_default_stacks(self):
        self.make_command_stack(
            source=self._svc.get_plugin_command_source(),
            name=self._cfg.on_server_start_sends,
            perm=3,
            desc=self._svc.tr('server_start_desc').to_plain_text()
        )

    @new_thread('check_perm_stacks')
    def check_perm_stacks(self):
        self._cmd_perm_task.check_stacks()

    @new_thread('reset_timed_stacks')
    def reset_timed_stacks(self):
        self._interval_send_task.reset_timed_stacks()

    def stop_timed_stacks(self):
        self._interval_send_task.stop_timed_stacks()
