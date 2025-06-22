from typing import List, Optional
from abc import ABC, abstractmethod
import os

from mcdreforged.api.all import *

from auto_command.context import Context


class CommandStack(Serializable):
    desc: Optional[str] = None
    perm: int = 3
    interval: str = '0'
    command: List[str] = []


class CommandStackStorage(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def first_load(self) -> bool:
        pass

    @abstractmethod
    def get(self, name: str) -> CommandStack:
        pass

    @abstractmethod
    def contains(self, name: str) -> bool:
        pass

    @abstractmethod
    def stack_names(self) -> List[str]:
        pass

    @abstractmethod
    def timed_stack_names(self) -> List[str]:
        pass

    @abstractmethod
    def search_stack(self, keyword: str) -> List[str]:
        pass

    @abstractmethod
    def add_stack(self, name: str, stack: CommandStack):
        pass

    @abstractmethod
    def pop_stack(self, name: str) -> CommandStack:
        pass

    @abstractmethod
    def add_command(self, name: str, command: str, line: int):
        pass

    @abstractmethod
    def edit_command(self, name: str, command: str, line: int):
        pass

    @abstractmethod
    def del_command(self, name: str, line: int):
        pass

    @abstractmethod
    def change_name(self, name: str, new_name: str):
        pass

    @abstractmethod
    def change_perm(self, name: str, level: int):
        pass

    @abstractmethod
    def change_interval(self, name: str, time: str):
        pass

    @abstractmethod
    def change_desc(self, name: str, desc: str):
        pass


class CommandStackStorageFactory:
    def __init__(self, ctx: Context):
        self._cfg = ctx.cfg
        self._svc = ctx.svc

    def get_command_stack_storage(self) -> CommandStackStorage:
        from auto_command.storage.storage_file import CommandStackFileStorage
        file_path = os.path.join(self._svc.get_data_folder(), self._cfg.command_stack_storage_file)
        return CommandStackFileStorage(file_path, self._svc.log_exception)
