import re
from typing import Dict, Callable
import asyncio

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage
from auto_command.task.edit_cmd_in_stack_task import EditCommandInStackTask
from auto_command.task.cmd_perm_task import CommandPermTask
from auto_command.exceptions import ACPermDeniedException


class RecordCommandStackTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage, edit_cmd_in_stack_task: EditCommandInStackTask, cmd_perm_task: CommandPermTask):
        self._cfg = ctx.cfg.record_command_stack_config
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._time = ctx.time
        self._storage = storage
        self._rec_users: Dict[str] = {}
        self._edit_cmd_in_stack_task = edit_cmd_in_stack_task
        self._cmd_perm_task = cmd_perm_task

    def _match_blacklist(self, cmd: str):
        for regex in self._cfg.command_blacklist:
            if regex.fullmatch(cmd):
                return True
        return False

    def stack_record(self, source: CommandSource, name: str):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            user = self._utils.get_user(source)

            rec_start: bool
            if user in self._rec_users:
                self._rec_users.pop(user)
                rec_start = False
            else:
                self._rec_users[user] = name
                rec_start = True
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_record.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to record command stack {}'.format(name))
        else:
            msg: RTextBase
            if rec_start:
                msg = self._svc.tr('stack_record.start', name)
            else:
                msg = self._svc.tr('stack_record.stop', name)

            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_record.success', msg, name), name))

    def on_user_info(self, info: Info):
        source = info.get_command_source()
        command = info.content
        user = self._utils.get_user(source)
        if user in self._rec_users and command is not None and not self._match_blacklist(command):
            if m := self._cfg.record_mc_command_regex.match(command):
                command = '/' + m.group(1)
                exec_command = command
                if re.match('/player (.*) spawn here', command):
                    command = self._utils.interpret_player_spawn(source, command)
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self._time.sleep(self._cfg.player_spawn_here_delay, 's'))
                    loop.close()
                elif re.fullmatch(r'/player (.*) spawn', command):
                    exec_command = self._utils.interpret_player_spawn(source, command)

                try:
                    self._cmd_perm_task.has_perm(source, command)
                except ACPermDeniedException:
                    pass
                else:
                    self._svc.exec_mc_cmd(exec_command)

            self._edit_cmd_in_stack_task.stack_add_command(source, self._rec_users[user], command)

