from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage


class InfoCommandStackTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage):
        self._cfg = ctx.cfg
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._storage = storage

    def info_command_stack(self, source: CommandSource, name: str):

        def const_info(lit: str, value):
            return RText(self._svc.tr(f'command_stack_info.{lit}.header', value)).\
            h(self._svc.tr(f'command_stack_info.{lit}.hover')).\
            c(RAction.suggest_command, f'{self._cfg.prefix} stack {name} {lit} {value}') +\
            '\n'

        stack = self._storage.get(name)
        self._svc.print(
            source,
            const_info('rename', name) +
            const_info('perm', stack.perm) +
            const_info('interval', stack.interval) +
            const_info('desc', stack.desc) +
            RText(self._svc.tr('command_stack_info.send.header')).
            h(self._svc.tr('command_stack_info.send.hover')).
            c(RAction.run_command, f'{self._cfg.prefix} send {name}') +
            '\n' +
            self._svc.tr('command_stack_info.text', stack.desc)
        )
        count = 0
        for command in stack.command:
            count += 1
            self._svc.print(
                source,
                f'[{str(count)}] ' +
                RText('[↑] ', color=RColor.green).
                h(self._svc.tr('command_stack_info.command.before')).
                c(RAction.suggest_command, f'{self._cfg.prefix} stack {name} before {count} ') +
                RText('[×] ', color=RColor.red).
                h(self._svc.tr('command_stack_info.command.delete')).
                c(RAction.run_command, f'{self._cfg.prefix} stack {name} del {count}') +
                RText(command, color=RColor.gray).
                h(self._svc.tr('command_stack_info.command.edit')).
                c(RAction.suggest_command, f'{self._cfg.prefix} stack {name} edit {count} {command}'),
            )
        self._svc.print(
            source,
            RText(self._svc.tr('command_stack_info.add.header')).
            h(self._svc.tr('command_stack_info.add.hover')).
            c(RAction.suggest_command, f'{self._cfg.prefix} stack {name} add ')
        )
        self._svc.print(
            source,
            RText(self._svc.tr('command_stack_info.record.header')).
            h(self._svc.tr('command_stack_info.record.hover')).
            c(RAction.run_command, f'{self._cfg.prefix} stack {name} record')
        )
