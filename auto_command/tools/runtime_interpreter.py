import re

from mcdreforged.api.all import *

from auto_command.context import Context


class RuntimeInterpreter:
    def __init__(self, source: CommandSource, ctx: Context):
        self._source = source
        self._utils = ctx.utils

    def _replace(self, match: re.Match) -> str:
        key = match.group(1)
        if key == '':
            return '$'
        elif key == 'userId':
            return self._utils.get_user(self._source)

    def interpret(self, cmd: str):
        return re.sub(r'\$(.*?)\$', self._replace, cmd)
