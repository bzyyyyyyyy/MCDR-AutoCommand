import re

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.tools.ac_time import ACTime
from auto_command.constant import DEFAULT_WAIT_UNIT


class HelpMessageTask:
    def __init__(self, ctx: Context):
        self._svc = ctx.svc
        self._cfg = ctx.cfg
        self._utils = ctx.utils

    def print_simple_help_message(self, source: CommandSource):
        self._print_help_message(source, mode='simple')

    def print_full_help_message(self, source: CommandSource):
        self._print_help_message(source, mode='full')
    
    def _print_help_message(self, source: CommandSource, mode: str = 'simple'):
        meta = self._svc.get_meta()
        help_message = self._svc.tr(f'help_message.{mode}', self._cfg.prefix, meta.name, meta.version, self._cfg.on_server_start_sends)
        for line in help_message.to_plain_text().splitlines():
            match = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(self._cfg.prefix), line)
            if match is not None:
                self._svc.print(
                    source,
                    RText(line).
                    h(self._svc.tr('help_message.hover', match.group())).
                    c(RAction.suggest_command, match.group())
                )
            else:
                if line.count(self._cfg.on_server_start_sends):
                    self._svc.print(source, self._utils.click_info(RText(line), self._cfg.on_server_start_sends))
                else:
                    self._svc.print(source, line)

    def print_wait_help(self, source: CommandSource, time: str):
        time = ACTime.to_time(time, DEFAULT_WAIT_UNIT)
        if ACTime.is_time_format(time):
            self._svc.print(source, self._svc.tr('help_message.wait', time))
        else:
            self._svc.print(source, self._svc.tr('fail_msg.time_format_mismatch', time))

    def print_perm_help(self, source: CommandSource, regex: str, white: bool = True):
        self._svc.print(source, self._svc.tr('help_message.perm.header', regex, self._svc.tr(f'help_message.perm.{"white" if white else "black"}')))
