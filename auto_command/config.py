import re
from typing import Optional, List

from mcdreforged.api.all import *

from auto_command.mcdr.mcdr_service import Service
from auto_command.constant import CONFIG_FILE


class TickDataGetterConfig(Serializable):
	gametime_command: str = 'time query gametime'
	gametime_output_regex: re.Pattern = re.compile(r'The time is (\d+)')
	tps_command: str = 'tick rate'
	tps_output_regex: re.Pattern = re.compile(r'Current tps is: (\d+(?:\.\d+)?)')


class CommandPermStacksConfig(Serializable):
	owner: str = 'command_perm_4'
	admin: str = 'command_perm_3'
	helper: str = 'command_perm_2'
	user: str = 'command_perm_1'
	guest: str = 'command_perm_0'

	def __getitem__(self, item: int) -> str:
		if item == 0:
			return self.guest
		elif item == 1:
			return self.user
		elif item == 2:
			return self.helper
		elif item == 3:
			return self.admin
		elif item == 4:
			return self.owner
		raise IndexError


class RecordCommandStackConfig(Serializable):
	record_mc_command_regex: re.Pattern = re.compile(r'^\./(.+)')
	player_spawn_here_delay: str = '20t'
	command_blacklist: List[re.Pattern] = [
		re.compile(r'^!!ac stack\s+(?:"[^"]+"|\S+)\s+record$')
	]


class Config(Serializable):
	prefix: str = '!!ac'
	command_stack_storage_file: str = 'command_stacks.json'
	on_server_start_sends: str = 'server_start'
	stack_per_page: int = 10
	tick_data_getter: TickDataGetterConfig = TickDataGetterConfig()
	command_perm_stacks: CommandPermStacksConfig = CommandPermStacksConfig()
	record_command_stack_config: RecordCommandStackConfig = RecordCommandStackConfig()

	@classmethod
	def get(cls, svc: Service):
		global _config
		if _config is None:
			_config = svc.load_config_simple(CONFIG_FILE, Config)
		return _config


_config: Optional[Config] = None
