import json
import os
from threading import RLock
from typing import List, Dict, Optional

from mcdreforged.api.all import *

from auto_command.constant import STORAGE_FILE


class CommandStack(Serializable):
    desc: Optional[str] = None
    perm: int
    command: List[str] = []


class CommandStackStorage:
    def __init__(self):
        self.stacks = {}  # type: Dict[str, CommandStack]
        self.__lock = RLock()

    def get(self, name: str) -> Optional[CommandStack]:
        with self.__lock:
            return self.stacks.get(name)

    def contains(self, name: str) -> bool:
        with self.__lock:
            return name in self.stacks

    def add_stack(self, name: str, stack: CommandStack) -> bool:
        with self.__lock:
            existed = self.get(name)
            if existed:
                return False
            else:
                self.stacks[name] = stack
                self.save()
                return True

    def change_command(self, name, command) -> bool:
        with self.__lock:
            stack = self.get(name)
            if not stack:
                return False
            else:
                self.stacks[name].command = command
                self.save()
                return True

    def change_perm(self, name: str, level) -> bool:
        with self.__lock:
            stack = self.get(name)
            if not stack:
                return False
            else:
                self.stacks[name].perm = level
                self.save()
                return True

    def del_stack(self, name: str) -> bool:
        with self.__lock:
            existed = self.get(name)
            if existed:
                self.stacks.pop(name)
                self.save()
                return True
            return False

    def load(self, file_path: str) -> bool:
        with self.__lock:
            folder = os.path.dirname(file_path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            self.stacks.clear()
            needs_overwrite = False
            if not os.path.isfile(file_path):
                needs_overwrite = True
            else:
                with open(file_path, 'r', encoding='utf8') as handle:
                    data = None
                    try:
                        data = json.load(handle)
                        stacks = deserialize(data, Dict[str, CommandStack])
                    except Exception as e:
                        from auto_command import server_inst
                        server_inst.logger.error(f'Fail to load {file_path}: {e}')
                        server_inst.logger.error(f'Unknown data: {data}')
                        needs_overwrite = True
                    else:
                        self.stacks = stacks
            if needs_overwrite:
                self.save()
        return needs_overwrite

    def save(self):
        from auto_command import server_inst
        with self.__lock:
            file_path = os.path.join(server_inst.get_data_folder(), STORAGE_FILE)
            with open(file_path, 'w', encoding='utf8') as file:
                json.dump(serialize(self.stacks), file, indent=4, ensure_ascii=False)
