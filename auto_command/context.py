from mcdreforged.api.all import *

from auto_command.mcdr.mcdr_service import Service
from auto_command.config import Config
from auto_command.utils import Utils
from auto_command.tools.tick_data_getter import TickDataGetter
from auto_command.tools.ac_time import ACTime
from auto_command.tools.info_getter import InfoGetter


class Context:
    def __init__(self, server: PluginServerInterface):
        self._svc = Service(server)
        self._cfg = Config.get(self.svc)
        self._utils = Utils(self._svc, self._cfg)
        self._tick_data_getter = TickDataGetter(self._svc, self._cfg.tick_data_getter)
        self._info_getter = InfoGetter(self._svc)
        self._time = ACTime(self._tick_data_getter)

    @property
    def svc(self):
        return self._svc

    @property
    def cfg(self):
        return self._cfg

    @property
    def utils(self):
        return self._utils

    @property
    def tick_data_getter(self):
        return self._tick_data_getter

    @property
    def info_getter(self):
        return self._info_getter

    @property
    def time(self):
        return self._time
