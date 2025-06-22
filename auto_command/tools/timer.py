import asyncio
import threading
import time
from typing import Callable, Coroutine, Optional

from mcdreforged.api.all import *


class FlexibleAsyncTimer:
    def __init__(self, callback: Callable):
        self._callback = callback
        self._wait_func = None
        self._task = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._reset_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._thread: Optional[threading.Thread] = None

    def _thread_main(self):
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        try:
            self._task = loop.create_task(self._run_loop())
            loop.run_forever()

        except Exception as e:
            pass
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())  # 清理 async gen
            except Exception as e:
                pass
            loop.close()

    @new_thread
    def start(self, wait_func: Callable[[], Coroutine]):
        self._wait_func = wait_func
        if self._thread and self._thread.is_alive():
            self._reset_event.set()
        else:
            self._stop_event.clear()
            self._reset_event.clear()
            self._thread = threading.Thread(target=self._thread_main, daemon=True)
            self._thread.start()

    @staticmethod
    def _shutdown_loop(loop: asyncio.AbstractEventLoop):
        def stopper():
            for task in asyncio.all_tasks(loop):
                task.cancel()
            loop.stop()

        loop.call_soon_threadsafe(stopper)

    def stop(self):
        self._stop_event.set()
        if self._loop and self._loop.is_running():
            self._shutdown_loop(self._loop)
        if self._thread and self._thread.is_alive():
            self._thread.join()

    async def _run_loop(self):
        try:
            while not self._stop_event.is_set():
                wait_task = asyncio.create_task(self._wait_func())
                loop = asyncio.get_running_loop()
                reset_task = loop.create_task(self._reset_event.wait())
                stop_task = loop.create_task(self._stop_event.wait())
                done, _ = await asyncio.wait(
                    [wait_task, reset_task, stop_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                if self._stop_event.is_set():
                    self._stop_event.clear()
                    self._reset_event.clear()
                    wait_task.cancel()
                    break
                elif self._reset_event.is_set():
                    self._stop_event.clear()
                    self._reset_event.clear()
                    wait_task.cancel()
                    continue
                elif wait_task in done:
                    self._callback()
                else:
                    break
        except Exception as e:
            pass
