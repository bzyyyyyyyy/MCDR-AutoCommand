import re

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage, CommandStack
from auto_command.exceptions import ACPermDeniedException, ACStackExistsException


class CommandPermTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage):
        self._svc = ctx.svc
        self._cfg = ctx.cfg
        self._perm_list = ctx.cfg.command_perm_stacks
        self._storage = storage

    def check_stacks(self):
        for i in range(5):
            if not self._storage.contains(self._perm_list[i]):
                stack = CommandStack(
                    desc=self._svc.tr('command_perm_desc', i).to_plain_text(),
                    perm=4
                )

                if i == 4:
                    stack.command = [
                        '{} white ^.*$'.format(self._cfg.prefix)
                    ]
                elif i == 3:
                    stack.command = [
                        '{} white ^.*$'.format(self._cfg.prefix),
                        '{} black ^/stop.*'.format(self._cfg.prefix),
                        '{} black ^/ban.*'.format(self._cfg.prefix)
                    ]
                elif i == 2:
                    stack.command = [
                        '{} white ^[^/].*'.format(self._cfg.prefix),
                        '{} white ^/player.*'.format(self._cfg.prefix),
                    ]
                elif i == 1:
                    stack.command = [
                        '{} white ^[^/].*'.format(self._cfg.prefix),
                    ]

                self._storage.add_stack(self._perm_list[i], stack)

    def has_perm(self, source: CommandSource, cmd: str):
        if not source.is_player:
            return
        source_level = source.get_permission_level()
        for level in range(4, source_level - 1, -1):
            white_passed = False
            stack = self._storage.get(self._perm_list[level])
            for line in stack.command:
                if m := re.fullmatch(r'^{} white\s+(.+)$'.format(self._cfg.prefix), line):
                    regex = m.group(1)
                    if re.match(regex, cmd):
                        white_passed = True
                elif m := re.fullmatch(r'^{} black\s+(.+)$'.format(self._cfg.prefix), line):
                    regex = m.group(1)
                    if re.match(regex, cmd):
                        raise ACPermDeniedException(level + 1, source_level)
            if not white_passed:
                raise ACPermDeniedException(level + 1, source_level)




