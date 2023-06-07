import time
from threading import Thread, Event

from mcdreforged.api.all import *

from auto_command.constant import Prefix


class TimedCommand(Thread):
	def __init__(self, server: PluginServerInterface):
		super().__init__()
		self.daemon = True
		self.name = self.__class__.__name__
		self.time_since_send = time.time()
		self.server = server
		self.stop_event = Event()
		self.is_enabled = False

	@staticmethod
	def __get_interval() -> float:
		from auto_command import config
		return config.timed_command_interval

	@classmethod
	def get_send_interval(cls):
		return cls.__get_interval() * 60

	def set_enabled(self, value: bool):
		self.is_enabled = value
		self.reset_timer()

	def reset_timer(self):
		self.time_since_send = time.time()

	def run(self):
		while True:
			while True:
				if self.stop_event.wait(1):
					return
				if time.time() - self.time_since_send > self.get_send_interval():
					break
			if self.is_enabled and self.server.is_server_startup():
				self.reset_timer()
				from auto_command import send_command_stack
				send_command_stack(self.server.get_plugin_command_source(), 'timed_command')

	def stop(self):
		self.stop_event.set()