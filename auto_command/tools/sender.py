from abc import ABC, abstractmethod
import re
import asyncio

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage
from auto_command.exceptions import ACRecursionException, ACUnknownStackException
from auto_command.constant import DEFAULT_WAIT_UNIT, COMMAND_TIMEOUT
from auto_command.tools.runtime_interpreter import RuntimeInterpreter


class CommandStackSender:
    def __init__(self, ctx: Context, source: CommandSource, storage: CommandStackStorage):
        self._cfg = ctx.cfg
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._info_getter = ctx.info_getter
        self._time = ctx.time
        self._source: CommandSource = source
        self._storage: CommandStackStorage = storage
        self._prev_send = []
        self._interpreter = RuntimeInterpreter(source, ctx)

    async def send_command_stack(self, name: str, condition='', unless=False):

        """
        exec_ac_cs(self, name: str)  catch error
            exec_mcdr_cmd(self, cmd: str)
                exec_ac_cmd(self, cmd: str)
                    exec_ac_cs(self, name: str)
                    exec_ac_wait(self, t: float)
                    exec_ac_if(self, name: str, condition: str, unless=False)
            exec_mc_cmd(self, cmd: str)
                exec_player_spawn(self, cmd: str)
            exec_msg(self, cmd: str)
        """

        try:
            if condition == '':
                await self._exec_ac_cs(name, show_success=False)
            else:
                await self._exec_ac_if(name, condition, unless, show_success=False)

            current = asyncio.current_task()
            await asyncio.gather(*[t for t in asyncio.all_tasks() if t is not current])
        except Exception as e:
            self._svc.print(self._source, self._svc.tr('send_command_stack.fail', name, self._utils.get_exception_msg(e)))
            self._svc.log_exception('Failed to send command stack {}'.format(name))
        else:
            self._svc.print(self._source, self._utils.click_info(RText(self._svc.tr('send_command_stack.success', name)), name), tell=False)

    async def _exec_ac_cs(self, name: str, show_success: bool = True):
        if not self._storage.contains(name):
            raise ACUnknownStackException(name)

        stack = self._storage.get(name)

        self._svc.req_perm(self._source, stack.perm)

        self._prev_send.append(name)
        if self._prev_send.count(name) == 2:
            raise ACRecursionException(name, self._prev_send)

        line = 0
        for cmd in stack.command:
            line += 1

            cmd = self._interpreter.interpret(cmd)

            try:
                if cmd[:2] == '!!':
                    await self._exec_mcdr_cmd(cmd)
                elif cmd[0] == '/':
                    await self._exec_mc_cmd(cmd)
                else:
                    await self._exec_msg(cmd)
            except Exception as e:
                self._svc.print(self._source, self._svc.tr('send_command_stack.fail_line', name, line, self._utils.get_exception_msg(e)))
                self._svc.log_exception('Failed sending command in stack: {} line: {}'.format(name, line))
        if show_success:
            self._svc.print(self._source, self._utils.click_info(RText(self._svc.tr('send_command_stack.success', name)), name), tell=False)

    async def _exec_mcdr_cmd(self, cmd: str):

        """
        exec_ac_cmd(self, cmd: str)
        """

        match_ac = re.match(r'^{}'.format(self._cfg.prefix), cmd)

        if match_ac:
            await self._exec_ac_cmd(cmd)
        else:
            self._svc.exec_mcdr_cmd(self._source, cmd)

    async def _exec_mc_cmd(self, cmd: str):
        match_player = re.match(r'^/player .+', cmd)
        if match_player:
            await self._exec_player(cmd)
        else:
            self._svc.exec_mc_cmd(cmd)

    async def _exec_player(self, cmd: str):
        match_player_spawn = re.match(r'^/player (.*) spawn', cmd)
        if match_player_spawn:
            await self._exec_player_spawn(cmd)
        else:
            self._svc.exec_mc_cmd(cmd)
            await self._time.sleep('1', 't')

    async def _exec_player_spawn(self, cmd: str):
        cmd = self._utils.interpret_player_spawn(self._source, cmd)
        self._svc.exec_mc_cmd(cmd)

    async def _exec_msg(self, cmd: str):
        self._svc.print(self._source, cmd, tell=False)

    async def _exec_ac_cmd(self, cmd: str):

        """
        exec_ac_cs(self, name: str)
        exec_ac_if(self, name: str, condition: str, unless=False)
        exec_ac_wait(self, t: float)
        """

        match_send = re.match(r'^{} send ("[^"]+"|\S+)(?:\s+(async))?(?:\s+(if|unless)\s+(.+))?$'.format(self._cfg.prefix), cmd)
        match_wait = re.match(r'^{} wait (\S+)'.format(self._cfg.prefix), cmd)
        if match_send:
            cs_name = match_send.group(1)
            is_async = match_send.group(2) == 'async'
            condition_type = match_send.group(3)  # 'if' or 'unless' or None
            condition_value = match_send.group(4)

            if cs_name.startswith('"') and cs_name.endswith('"'):
                cs_name = cs_name[1:-1]

            func = self._exec_ac_cs(cs_name)
            if condition_type == 'if' or condition_type == 'unless':
                func = self._exec_ac_if(cs_name, condition_value, condition_type == 'unless')

            if is_async:
                asyncio.create_task(func)
            else:
                await func

        elif match_wait:
            await self._exec_ac_wait(match_wait.group(1))

        else:
            self._svc.exec_mcdr_cmd(self._source, cmd)

    async def _exec_ac_if(self, name: str, condition: str, unless=False, show_success=True):
        if self._info_getter.if_condition(COMMAND_TIMEOUT, condition, unless):
            await self._exec_ac_cs(name, show_success)

    async def _exec_ac_wait(self, t: str):
        await self._time.sleep(t, DEFAULT_WAIT_UNIT)
