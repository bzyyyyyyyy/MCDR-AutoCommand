from typing import Callable

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorageFactory
from auto_command.task.task_manager import TaskManager
from auto_command.mcdr.mcdr_command import CommandManager


_task_manager: TaskManager
_ctx: Context
debug_loger: Callable[[str], None]


def on_load(server: PluginServerInterface, old):
    global _task_manager, _ctx, debug_loger

    _ctx = Context(server)
    debug_loger = _ctx.svc.log_info
    cmd_stack_storage = CommandStackStorageFactory(_ctx).get_command_stack_storage()
    _task_manager = TaskManager(_ctx, cmd_stack_storage)
    cmd_manager = CommandManager(_ctx, _task_manager)

    cmd_stack_storage.load()
    if cmd_stack_storage.first_load():
        _task_manager.const_default_stacks()
    _task_manager.check_perm_stacks()

    cmd_manager.construct_command_tree()

    if server.is_server_startup():
        _task_manager.reset_timed_stacks()


def on_info(server: PluginServerInterface, info):
    _ctx.tick_data_getter.on_info(info)
    _ctx.info_getter.on_info(info)


def on_user_info(server: PluginServerInterface, info: Info):
    _task_manager.on_user_info(info)


def on_server_startup(server: PluginServerInterface):
    _task_manager.reset_timed_stacks()
    _task_manager.send_command_stack(server.get_plugin_command_source(), _ctx.cfg.on_server_start_sends)


def on_unload(server: PluginServerInterface):
    _task_manager.stop_timed_stacks()


def on_remove(server: PluginServerInterface):
    _task_manager.stop_timed_stacks()
