import os
import re
from typing import Any, Optional
from math import ceil
import time

from mcdreforged.api.all import *

from auto_command.constant import Prefix, CONFIG_FILE, STORAGE_FILE
from auto_command.storage import CommandStackStorage, CommandStack
from auto_command.clock import TimedCommand


class Config(Serializable):
	minimum_stack_edit_perm: int = 3
	stack_per_page: int = 10
	time_after_execute: float = 0.1
	timed_command_interval: float = 30.0
	timed_command_enabled: bool = True



config: Config
storage = CommandStackStorage()
server_inst: PluginServerInterface
HelpMessage: RTextBase
clock = None  # type: Optional[TimedCommand]


def tr(translation_key: str, *args) -> RTextMCDRTranslation:
	return ServerInterface.get_instance().rtr(f'auto_command.{translation_key}', *args)


def print_message(source: CommandSource, msg, tell=True, prefix: Any = '[AC] '):
	msg = RTextList(prefix, msg)
	if source.is_player and not tell:
		source.get_server().say(msg)
	else:
		source.reply(msg)


def save_config():
	server_inst.save_config_simple(config, CONFIG_FILE)


def command_run(message: Any, text: Any, command: str) -> RTextBase:
	fancy_text = message.copy() if isinstance(message, RTextBase) else RText(message)
	return fancy_text.set_hover_text(text).set_click_event(RAction.run_command, command)


def print_help_message(source: CommandSource):
	if source.is_player:
		source.reply('')
	with source.preferred_language_context():
		for line in HelpMessage.to_plain_text().splitlines():
			prefix = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(Prefix), line)
			if prefix is not None:
				print_message(source, RText(line).set_click_event(RAction.suggest_command, prefix.group()), prefix='')
			else:
				print_message(source, line, prefix='')


def print_unknown_argument_message(source: CommandSource, error: UnknownArgument):
	print_message(source, command_run(
		tr('unknown_command.text', Prefix),
		tr('unknown_command.hover'),
		Prefix
	))


def req_perm(source: CommandSource, perm):
	if source.is_player and not source.has_permission(perm):
		source.reply(tr('command.permission_denied'))
		return True
	return False


def info_command_stack(source: CommandSource, name):
	stack = storage.get(name)
	if stack is not None:
		print_message(
			source,
			tr('command_stack_info.name', name) +
			'\n' +
			RText(tr('command_stack_info.perm.header', stack.perm)).
				h(tr('command_stack_info.perm.hover')).
				c(RAction.suggest_command, f'{Prefix} stack {name} perm ') +
			'\n' +
			tr('command_stack_info.desc', stack.desc) +
			'\n' +
			RText(tr('command_stack_info.send.header', stack.perm)).
				h(tr('command_stack_info.send.hover')).
				c(RAction.run_command, f'{Prefix} send {name}') +
			'\n' +
			tr('command_stack_info.text', stack.desc),
			prefix=''
		)
		count = 0
		for command in stack.command:
			count += 1
			print_message(
				source,
				f'[{str(count)}] ' +
				RText('[↑] ', color=RColor.green).
					h(tr('command_stack_info.command.before')).
					c(RAction.suggest_command, f'{Prefix} stack {name} before {count} ') +
				RText('[×] ', color=RColor.red).
					h(tr('command_stack_info.command.delete')).
					c(RAction.run_command, f'{Prefix} stack {name} del {count}') +
				RText(command, color=RColor.gray).
					h(tr('command_stack_info.command.edit')).
					c(RAction.suggest_command, f'{Prefix} stack {name} edit {count} {command}'),
				prefix=''
			)
		print_message(
			source,
			RText(tr('command_stack_info.add.header')).
			h(tr('command_stack_info.add.hover')).
			c(RAction.suggest_command, f'{Prefix} stack {name} add '),
			prefix=''
		)
	else:
		print_message(source, tr('command.unknown_command_stack', name))


def add_command_stack(source: CommandSource, name, perm: int, desc=None):
	if storage.contains(name):
		print_message(source, tr('make_command_stack.exist', name))
		return
	if req_perm(source, perm):
		return
	try:
		stack = CommandStack(desc=desc, perm=perm)
		storage.add_stack(name, stack)
	except Exception as e:
		print_message(source, tr('make_command_stack.fail', name, e))
		server_inst.logger.exception('Failed to add command stack {}'.format(name))
	else:
		print_message(
			source,
			RText(tr('make_command_stack.success', name)).
			h(tr('command_stack_info.display')).
			c(RAction.run_command, f'{Prefix} stack {name}')
		)


def use_interpreter(source: CommandSource, command):
	if re.match('/player (.*) spawn here', command):
		command = interpreter(source, command)
	return command


@new_thread('add_command')
def stack_add_command(source: CommandSource, name, command: str, line=0):
	if storage.contains(name):
		stack = storage.get(name)
		if req_perm(source, stack.perm):
			return
		try:
			commands = stack.command
			if line and line < (len(commands) + 1):
				line -= 1
			else:
				line = len(commands)
			command = use_interpreter(source, command)
			commands.insert(line, command)
			storage.change_command(name, commands)
		except Exception as e:
			print_message(source, tr('stack_add_command.fail', name, e))
			server_inst.logger.exception('Failed to add command to stack {} line {}'.format(name, line))
		else:
			print_message(
				source,
				RText(tr('stack_add_command.success', name, (line + 1))).
				h(tr('command_stack_info.display')).
				c(RAction.run_command, f'{Prefix} stack {name}')
			)
	else:
		print_message(source, tr('stack_add_command.unknown_stack', name))


@new_thread('edit_command')
def stack_edit_command(source: CommandSource, name, command: str, line: int):
	if storage.contains(name):
		stack = storage.get(name)
		if req_perm(source, stack.perm):
			return
		try:
			commands = stack.command
			command = use_interpreter(source, command)
			commands[line-1] = command
			storage.change_command(name, commands)
		except Exception as e:
			print_message(source, tr('stack_edit_command.fail', name, e))
			server_inst.logger.exception('Failed to edit command in stack {} line {}'.format(name, line))
		else:
			print_message(
				source,
				RText(tr('stack_edit_command.success', name, line)).
				h(tr('command_stack_info.display')).
				c(RAction.run_command, f'{Prefix} stack {name}')
			)
	else:
		print_message(source, tr('stack_edit_command.unknown_stack', name))


def stack_del_command(source: CommandSource, name, line=0):
	if storage.contains(name):
		stack = storage.get(name)
		if req_perm(source, stack.perm):
			return
		try:
			commands = stack.command
			if not line:
				line = len(commands)
			commands.pop(line - 1)
			storage.change_command(name, commands)
		except Exception as e:
			print_message(source, tr('stack_del_command.fail', name, e))
			server_inst.logger.exception('Failed to delete command in stack {} line {}'.format(name, line))
		else:
			print_message(
				source,
				RText(tr('stack_del_command.success', name, line)).
				h(tr('command_stack_info.display')).
				c(RAction.run_command, f'{Prefix} stack {name}')
			)
	else:
		print_message(source, tr('stack_del_command.unknown_stack', name))


def stack_perm(source: CommandSource, name, level: int):
	if storage.contains(name):
		stack = storage.get(name)
		if source.is_player and (not source.has_permission(stack.perm) or not source.has_permission(level)):
			source.reply(tr('command.permission_denied'))
			return
		try:
			storage.change_perm(name, level)
		except Exception as e:
			print_message(source, tr('stack_perm.fail', name, e))
			server_inst.logger.exception('Failed to change permission of stack {}'.format(name))
		else:
			print_message(
				source,
				RText(tr('stack_perm.success', name)).
				h(tr('command_stack_info.display')).
				c(RAction.run_command, f'{Prefix} stack {name}')
			)
	else:
		print_message(source, tr('stack_perm.unknown_stack', name))


def del_command_stack(source: CommandSource, name):
	if storage.contains(name):
		stack = storage.get(name)
		if req_perm(source, stack.perm):
			return
		try:
			storage.del_stack(name)
		except Exception as e:
			print_message(source, tr('del_command_stack.fail', name, e))
			server_inst.logger.exception('Failed to delete command stack {}'.format(name))
		else:
			print_message(source, tr('del_command_stack.success', name))
	else:
		print_message(source, tr('del_command_stack.unknown_stack', name))


def interpreter(source: CommandSource, command: str, execute_as_player=False) -> str:

	carpet_bot = re.match('/player (.*) spawn', command)
	if carpet_bot and isinstance(source, PlayerCommandSource):
		api = source.get_server().get_plugin_instance('minecraft_data_api')
		pos = api.get_player_coordinate(source.player)
		face = api.get_player_info(source.player, 'Rotation')
		dims = ['overworld', 'the_end', 'the_nether']
		dim = dims[api.get_player_dimension(source.player)]
		gamemodes = ['survival', 'creative', 'adventure', 'spectator']
		gamemode = gamemodes[api.get_player_info(source.player, 'playerGameType')]
		bot = carpet_bot.group(1)
		nodes = command.split(' ')
		if len(nodes) > 4 and nodes[3] == 'in':
			gamemode = nodes[4]
		elif len(nodes) > 6 and nodes[3] == 'at':
			pos = nodes[4:7]
			if len(nodes) > 9 and nodes[7] == 'facing':
				face = nodes[8:10]
				if len(nodes) > 11 and nodes[10] == 'in':
					dim = nodes[11]
					if len(nodes) > 13 and nodes[12] == 'in':
						gamemode = nodes[13]
		faceing = f'{face[0]} {face[1]}'
		if execute_as_player:
			command = f'/execute as {source.player} run player {bot} spawn at {pos[0]} {pos[1]} {pos[2]} facing {faceing} in {dim} in {gamemode}'
		else:
			command = f'/player {bot} spawn at {pos[0]} {pos[1]} {pos[2]} facing {faceing} in {dim} in {gamemode}'

	return command


class Sender:
	def __init__(self, source: CommandSource):
		self.prev_send = []
		self.source = source
		self.nested_loops = []

	def send_commands(self, name):
		self.prev_send.append(name)
		if storage.contains(name):
			if self.prev_send.count(name) == 2:
				names = ''
				for sended in self.prev_send:
					if sended == name:
						names += f'§c{sended}§r'
					else:
						names += sended
					names += ' §6->§r '
				self.nested_loops.append(names[:-8])
				return
			stack = storage.get(name)
			if req_perm(self.source, stack.perm):
				return
			try:
				line = 0
				for command in stack.command:
					line += 1
					if command[:2] == '!!':
						if command[:9] == '!!ac send':
							self.send_commands(command[10:])
							self.prev_send.pop()
						elif command[:9] == '!!ac wait':
							try:
								time.sleep(float(command[10:]))
							except:
								print_message(self.source, tr('wait.fail', name, line, '!!ac wait', command[10:]))
						else:
							print(command)
							server_inst.execute_command(command, self.source)
					elif command[0] == '/':
						command = interpreter(self.source, command, execute_as_player=True)
						server_inst.execute(command)
						time.sleep(config.time_after_execute)
					else:
						server_inst.say(command)
			except Exception as e:
				print_message(self.source, tr('send_command_stack.fail', name, e))
				server_inst.logger.exception('Failed to send command stack {}'.format(name))
			else:
				print_message(
					self.source,
					RText(tr('send_command_stack.success', name)).
					h(tr('command_stack_info.display')).
					c(RAction.run_command, f'{Prefix} stack {name}'),
					tell=False
				)
		else:
			print_message(self.source, tr('send_command_stack.unknown_stack', name))

	def if_nested_loop(self):
		if self.nested_loops:
			for loop in self.nested_loops:
				print_message(self.source, tr('send_command_stack.nested_loop', loop))


@new_thread('send_command')
@spam_proof
def send_command_stack(source: CommandSource, name):
	s = Sender(source)
	s.send_commands(name)
	s.if_nested_loop()


def list_command_stack(source: CommandSource, *, keyword: Optional[str] = None, page: Optional[int] = None):
	matched_stacks = []
	stacks = storage.stacks
	for name in stacks:
		if keyword is None or name.find(keyword) != -1 or (stacks[name].desc is not None and stacks[name].desc.find(keyword) != -1):
			matched_stacks.append(name)
	matched_count = len(matched_stacks)
	page_count = ceil(matched_count / config.stack_per_page)
	if keyword is None:
		lit = 'list'
	else:
		lit = 'search'
	def line(stack_name):
		return RTextList(
				RText('[▷]', RColor.green).h(tr('command_stack_info.send.hover')).c(RAction.run_command, f'{Prefix} send {stack_name}'),
				RText(f' {stack_name} ', RColor.gold).h(tr('command_stack_info.display')).c(RAction.run_command, f'{Prefix} stack {stack_name}'),
				RText(stacks[stack_name].perm, RColor.light_purple).h(tr('list_command_stack.perm_hover')),
				RText(' [i]', RColor.gray).h(stacks[stack_name].desc)
			)
	if page is None:
		for name in matched_stacks:
			print_message(source, line(name), prefix=RText('- ', color=RColor.gray))
	else:
		if page > page_count:
			page = page_count
		left, right = (page - 1) * config.stack_per_page, page * config.stack_per_page
		for i in range(left, right):
			if 0 <= i < matched_count:
				print_message(source, line(matched_stacks[i]), prefix=RText('- ', color=RColor.gray))

		has_prev = page != 1
		has_next = page != page_count
		color = {False: RColor.dark_gray, True: RColor.gray}
		if keyword is None:
			keyword = ''
		else:
			keyword += ' '

		prev_page = RText('<-', color=color[has_prev])
		if has_prev:
			prev_page.h(tr('list_command_stack.page_prev.Y')). \
				c(RAction.run_command, f'{Prefix} {lit} {keyword}{page - 1}')
		else:
			prev_page.h(tr('list_command_stack.page_prev.N'))

		next_page = RText('->', color=color[has_next])
		if has_next:
			next_page.h(tr('list_command_stack.page_next.Y')). \
				c(RAction.run_command, f'{Prefix} {lit} {keyword}{page + 1}')
		else:
			next_page.h(tr('list_command_stack.page_next.N'))

		source.reply(RTextList(
			prev_page,
			f' §a{page}§r/§a{page_count} ',
			next_page
		))
	print_message(source, tr(f'list_command_stack.count.{lit}', matched_count), prefix='')


def tc_set_enabled(source: CommandSource, value: bool):
	stack = storage.get('timed_command')
	if req_perm(source, stack.perm):
		return
	config.timed_command_enabled = value
	clock.set_enabled(value)
	save_config()
	print_message(source, tr('tc.set_enabled.timer', tr('tc.set_enabled.start') if value else tr('tc.set_enabled.stop')))


def tc_set_interval(source: CommandSource, minute: float):
	stack = storage.get('timed_command')
	if req_perm(source, stack.perm):
		return
	config.timed_command_interval = minute
	save_config()
	storage.stacks['timed_command'].desc = tr('timed_command_desc', config.timed_command_interval).to_plain_text()
	print_message(source, tr('tc.set_interval', config.timed_command_interval))


def tc_reset_timer(source: CommandSource):
	stack = storage.get('timed_command')
	if req_perm(source, stack.perm):
		return
	clock.reset_timer()
	print_message(source, tr('tc.reset_timer'))


def register_command(server: PluginServerInterface):
	def req_edit_perm(literal):
		return Literal(literal).\
			   requires(lambda src: src.has_permission(config.minimum_stack_edit_perm)).\
			   on_error(RequirementNotMet, lambda src: src.reply(tr('command.permission_denied')), handled=True)
	server.register_command(
		Literal(Prefix).
		runs(print_help_message).
		on_error(UnknownArgument, print_unknown_argument_message, handled=True).
		then(req_edit_perm('make').then(QuotableText('name').then(Integer('perm').in_range(0, 4).
			runs(lambda src, ctx: add_command_stack(src, ctx['name'], ctx['perm'])).
			then(GreedyText('desc').
				runs(lambda src, ctx: add_command_stack(src, ctx['name'], ctx['perm'], ctx['desc']))
			)
		))).
		then(Literal('stack').then(QuotableText('name').
			runs(lambda src, ctx: info_command_stack(src, ctx['name'])).
			then(req_edit_perm('add').then(GreedyText('command').
				runs(lambda src, ctx: stack_add_command(src, ctx['name'], ctx['command']))
			)).
			then(req_edit_perm('before').then(Integer('line').at_min(1).then(GreedyText('command').
				runs(lambda src, ctx: stack_add_command(src, ctx['name'], ctx['command'], ctx['line']))
			))).
			then(req_edit_perm('edit').then(Integer('line').at_min(1).then(GreedyText('command').
				runs(lambda src, ctx: stack_edit_command(src, ctx['name'], ctx['command'], ctx['line']))
			))).
			then(req_edit_perm('del').
				runs(lambda src, ctx: stack_del_command(src, ctx['name'])).
				then(Integer('line').at_min(1).
					runs(lambda src, ctx: stack_del_command(src, ctx['name'], ctx['line']))
				)
			).
			then(req_edit_perm('perm').then(Integer('level').in_range(0, 4).
				runs(lambda src, ctx: stack_perm(src, ctx['name'], ctx['level']))
			))
		)).
		then(Literal('send').then(QuotableText('name').
			runs(lambda src, ctx: send_command_stack(src, ctx['name']))
		)).
		then(req_edit_perm('del').then(QuotableText('name').
			runs(lambda src, ctx: del_command_stack(src, ctx['name']))
		)).
		then(Literal('list').
			runs(lambda src: list_command_stack(src)).
			then(Integer('page').at_min(1).
				runs(lambda src, ctx: list_command_stack(src, page=ctx['page']))
			)
		).
		then(Literal('search').then(QuotableText('keyword').
			runs(lambda src, ctx: list_command_stack(src, keyword=ctx['keyword'])).
			then(Integer('page').at_min(1).
				runs(lambda src, ctx: list_command_stack(src, keyword=ctx['keyword'], page=ctx['page']))
			)
		)).
		then(Literal('wait').then(Float('sec').at_min(0.05).
			runs(lambda src: print_message(src, tr('wait.help')))
		)).
		then(Literal('tc').
			runs(lambda src: info_command_stack(src, 'timed_command')).
			then(Literal('enable').
				runs(lambda src: tc_set_enabled(src, True))
			).
			then(Literal('disable').
				runs(lambda src: tc_set_enabled(src, False))
			).
			then(Literal('set_interval').then(Float('minute').at_min(0.1).
				runs(lambda src, ctx: tc_set_interval(src, ctx['minute']))
			)).
			then(Literal('reset_timer').
				runs(lambda src: tc_reset_timer(src))
			)
		)
	)


def on_load(server: PluginServerInterface, old):
	global config, HelpMessage, server_inst, clock
	server_inst = server
	meta = server.get_self_metadata()
	HelpMessage = tr('help_message', Prefix, meta.name, meta.version)
	config = server.load_config_simple(CONFIG_FILE, target_class=Config)
	if storage.load(os.path.join(server.get_data_folder(), STORAGE_FILE)):
		add_command_stack(server.get_plugin_command_source(), 'server_start', 3, tr('server_start_desc').to_plain_text())
		add_command_stack(server.get_plugin_command_source(), 'timed_command', 3, tr('timed_command_desc', config.timed_command_interval).to_plain_text())
	clock = TimedCommand(server)
	try:
		clock.time_since_send = float(old.clock.time_since_send)
	except (AttributeError, ValueError):
		pass
	clock.set_enabled(config.timed_command_enabled)
	clock.start()
	register_command(server)
	server.register_help_message(Prefix, command_run(tr('register.summary_help'), tr('register.show_help'), Prefix))


def on_server_startup(server: PluginServerInterface):
	send_command_stack(server.get_plugin_command_source(), 'server_start')


def on_unload(server: PluginServerInterface):
	server.logger.info(tr('tc.on_unload'))
	clock.stop()


def on_remove(server):
	server.logger.info(tr('tc.on_remove'))
	clock.stop()