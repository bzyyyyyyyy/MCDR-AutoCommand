from typing import List, Optional, Type, Callable, Any
from abc import ABC, abstractmethod

from mcdreforged.api.all import *


class ACExceptionBase(Exception):
    @property
    @abstractmethod
    def translation_key(self) -> str:
        pass

    @property
    @abstractmethod
    def args(self) -> tuple:
        pass



class ACException(ACExceptionBase):
    def __init__(self, translation_key: str, *args):
        self._translation_key = translation_key
        self._args = args

    @property
    def translation_key(self) -> str:
        return self._translation_key

    @property
    def args(self) -> tuple:
        return self._args


class ACUnknownStackException(ACExceptionBase):
    def __init__(self, name: str):
        self._name = name

    @property
    def translation_key(self) -> str:
        return 'fail_msg.unknown_stack'

    @property
    def args(self) -> tuple:
        return (self._name,)

    def __str__(self):
        return f'Unknown command stack "{self._name}"'


class ACStackExistsException(ACExceptionBase):
    def __init__(self, name: str):
        self._name = name

    @property
    def translation_key(self) -> str:
        return 'fail_msg.stack_exists'

    @property
    def args(self) -> tuple:
        return (self._name,)

    def __str__(self):
        return f'"{self._name}" already exists'


class ACPermDeniedException(ACExceptionBase):
    def __init__(self, req: int, cur: int):
        self._req = req
        self._cur = cur

    @property
    def translation_key(self) -> str:
        return 'fail_msg.permission_denied'

    @property
    def args(self) -> tuple:
        return self._req, self._cur

    def __str__(self):
        return f'Requires permission {self._req}, but get permission {self._cur}'


class ACRecursionException(ACExceptionBase):
    def __init__(self, name, prev_send):
        self._name = name
        self._recursion: List[RText] = []
        for sent in prev_send:
            color = RColor.white
            if sent == name:
                color = RColor.red
            self._recursion.append(RText(sent, color=color))

    @property
    def translation_key(self) -> str:
        return 'fail_msg.recursion'

    @property
    def args(self) -> tuple:
        return (self._recursion,)

    def __str__(self):
        return f'Detected recursion in command stack "{self._name}"'


class ACTimeFormatMismatchException(ACExceptionBase):
    def __init__(self, time: str):
        self._time = time

    @property
    def translation_key(self) -> str:
        return 'fail_msg.time_format_mismatch'

    @property
    def args(self) -> tuple:
        return (self._time,)

    def __str__(self):
        return f'Incorrect time format: {self._time}'


class ACGetGametickTimeoutException(ACExceptionBase):

    @property
    def translation_key(self) -> str:
        return 'fail_msg.get_gametick_timeout'

    @property
    def args(self) -> tuple:
        return ()

    def __str__(self):
        return 'Timeout when getting gametick'


class ACZeroTimeIntervalException(ACExceptionBase):

    @property
    def translation_key(self) -> str:
        return 'fail_msg.zero_time_interval'

    @property
    def args(self) -> tuple:
        return ()

    def __str__(self):
        return 'Time interval could not be 0'
