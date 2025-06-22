from typing import List, Optional, Type, Callable, Any, Union

from mcdreforged.api.all import *

from auto_command.exceptions import ACPermDeniedException
from auto_command.constant import PLUGIN_ID


class Service:
    def __init__(self, server: PluginServerInterface):
        self._server: PluginServerInterface = server

    def exec_mc_cmd(self, command: str):
        self._server.execute(command)

    def exec_mcdr_cmd(self, source: CommandSource, command: str):
        self._server.execute_command(command, source)

    def print(self, source: CommandSource, msg: Any, tell=True, prefix: Any = ''):
        msg = RTextList(prefix, msg)
        if not tell:
            self._server.broadcast(msg)
        else:
            source.reply(msg)


    def say(self, msg: str):
        self._server.say(msg)

    def log_exception(self, msg: str):
        self._server.logger.exception(msg)

    def log_info(self, msg: str):
        self._server.logger.info(msg)

    def tr(self, translation_key: str, *args) -> RTextMCDRTranslation:
        return self._server.rtr(f'{PLUGIN_ID}.{translation_key}', *args)

    def tr_en(self, translation_key: str, *args) -> RTextBase:
        return self._server.tr(translation_key, args, _mcdr_tr_language='en_us')

    def save_config(self, config: dict | Serializable, file: str):
        self._server.save_config_simple(config, file)

    def req_perm(self, source: CommandSource, perm: int):
        if source.is_player and not source.has_permission(perm):
            raise ACPermDeniedException(perm, source.get_permission_level())

    def get_mc_data_api(self) -> Any:
        return self._server.get_plugin_instance('minecraft_data_api')

    def get_meta(self) -> Metadata:
        return self._server.get_self_metadata()

    def load_config_simple(self, file_name, target_class):
        return self._server.load_config_simple(file_name, target_class=target_class)

    def register_command(self, root_node: Literal):
        self._server.register_command(root_node)

    def get_data_folder(self) -> str:
        return self._server.get_data_folder()

    def get_plugin_command_source(self) -> PluginCommandSource:
        return self._server.get_plugin_command_source()
