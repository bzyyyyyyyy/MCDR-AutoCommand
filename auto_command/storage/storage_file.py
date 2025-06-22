import json
import os
from threading import RLock
from typing import List, Dict, Callable

from mcdreforged.api.all import *

from auto_command.storage.storage import CommandStackStorage, CommandStack
from auto_command.exceptions import ACUnknownStackException, ACStackExistsException
from auto_command.tools.ac_time import ACTime


class CommandStackFileStorage(CommandStackStorage):

    def __init__(self, file_path: str, log_callback: Callable[[str], None]):
        self._log_callback: Callable[[str], None] = log_callback
        self._file_path: str = file_path
        self._stacks: Dict[str, CommandStack] = {}
        self._first_load: bool = False
        self.__lock = RLock()

    def _save(self):
        with open(self._file_path, 'w', encoding='utf8') as file:
            json.dump(serialize(self._stacks), file, indent=4, ensure_ascii=False)

    def load(self):
        with self.__lock:
            folder = os.path.dirname(self._file_path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            self._stacks.clear()
            needs_overwrite = False
            if not os.path.isfile(self._file_path):
                needs_overwrite = True
            else:
                with open(self._file_path, 'r', encoding='utf8') as handle:
                    data = None
                    try:
                        data = json.load(handle)
                        stacks = deserialize(data, Dict[str, CommandStack])
                    except Exception as e:
                        self._log_callback(f'Fail to load {self._file_path}: {e}')
                        self._log_callback(f'Unknown data: {data}')
                        needs_overwrite = True
                    else:
                        self._stacks = stacks
            if needs_overwrite:
                self._save()
            self._first_load = needs_overwrite

    def first_load(self) -> bool:
        with self.__lock:
            return self._first_load

    def _assert_exists(self, name: str):
        if not self.contains(name):
            raise ACUnknownStackException(name)

    def _assert_not_exists(self, name: str):
        if self.contains(name):
            raise ACStackExistsException(name)

    def get(self, name: str) -> CommandStack:
        with self.__lock:
            self._assert_exists(name)
            return self._stacks.get(name)

    def contains(self, name: str) -> bool:
        with self.__lock:
            return name in self._stacks

    def stack_names(self) -> List[str]:
        with self.__lock:
            return list(self._stacks.keys())

    def timed_stack_names(self) -> List[str]:
        with self.__lock:
            timed_stack_names = []
            for name in self._stacks:
                if ACTime.not_zero(self._stacks[name].interval):
                    timed_stack_names.append(name)
            return timed_stack_names

    def search_stack(self, keyword: str) -> List[str]:
        with self.__lock:
            matched_names = []
            for name in self._stacks:
                if name.find(keyword) != -1 or (self._stacks[name].desc is not None and self._stacks[name].desc.find(keyword) != -1):
                    matched_names.append(name)
            return matched_names

    def add_stack(self, name: str, stack: CommandStack):
        with self.__lock:
            self._assert_not_exists(name)
            self._stacks[name] = stack
            self._save()

    def pop_stack(self, name: str) -> CommandStack:
        with self.__lock:
            self._assert_exists(name)
            stack = self._stacks.pop(name)
            self._save()
            return stack

    def add_command(self, name: str, command: str, line: int):
        with self.__lock:
            stack = self.get(name)
            stack.command.insert(line, command)
            self._save()

    def edit_command(self, name: str, command: str, line: int):
        with self.__lock:
            stack = self.get(name)
            stack.command[line] = command
            self._save()

    def del_command(self, name: str, line: int):
        with self.__lock:
            stack = self.get(name)
            stack.command.pop(line)
            self._save()

    def change_name(self, name: str, new_name: str):
        with self.__lock:
            stack = self.pop_stack(name)
            self.add_stack(new_name, stack)
            self._save()

    def change_perm(self, name: str, level: int):
        with self.__lock:
            stack = self.get(name)
            stack.perm = level
            self._save()

    def change_interval(self, name: str, time: str):
        with self.__lock:
            stack = self.get(name)
            stack.interval = time
            self._save()

    def change_desc(self, name: str, desc: str):
        with self.__lock:
            stack = self.get(name)
            stack.desc = desc
            self._save()
