from typing import Optional
import re

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage, CommandStack
from auto_command.exceptions import ACUnknownStackException
from auto_command.task.cmd_perm_task import CommandPermTask


class EditCommandInStackTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage, cmd_perm_task: CommandPermTask):
        self._cfg = ctx.cfg
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._storage = storage
        self._cmd_perm_task = cmd_perm_task

    def _check_ac_perm(self, source: CommandSource, command: str):
        if m := re.match(r'^({0}|/{0}) (send|make|del|stack)\s+(".*?"|\S+)'.format(self._cfg.prefix), command):
            raw_name = m.group(3)
            name = raw_name[1:-1] if raw_name.startswith('"') else raw_name
            try:
                stack = self._storage.get(name)
            except ACUnknownStackException:
                pass
            else:
                self._utils.req_perm(source, stack.perm)


    def stack_add_command(self, source: CommandSource, name: str, command: str, line: int = 0):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            self._check_ac_perm(source, command)

            self._cmd_perm_task.has_perm(source, command)

            if not (line and line < (len(stack.command) + 1)):
                line = len(stack.command) + 1

            if re.match('/player (.*) spawn here', command):
                command = self._utils.interpret_player_spawn(source, command)

            self._storage.add_command(name, command, line - 1)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_add_command.fail', self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to add command to stack {} line {}'.format(name, line))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_add_command.success', name, line), name))

    def stack_edit_command(self, source: CommandSource, name: str, command: str, line: int):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            self._check_ac_perm(source, command)

            self._cmd_perm_task.has_perm(source, command)

            if re.match('/player (.*) spawn here', command):
                command = self._utils.interpret_player_spawn(source, command)

            self._storage.edit_command(name, command, line - 1)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_edit_command.fail', self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to edit command in stack {} line {}'.format(name, line))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_edit_command.success', name, line), name))

    def stack_del_command(self, source: CommandSource, name: str, line: Optional[int] = None):
        try:
            stack = self._storage.get(name)
            self._utils.req_perm(source, stack.perm)

            if not line:
                line = len(stack.command)

            self._storage.del_command(name, line - 1)
        except Exception as e:
            self._svc.print(source, self._svc.tr('stack_del_command.fail', self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to delete command in stack {} line {}'.format(name, line))
        else:
            self._svc.print(source, self._utils.click_info(self._svc.tr('stack_del_command.success', name, line), name))
