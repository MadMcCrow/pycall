#!/usr/bin/env python
# Class to display a simple throbber

# python
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TypeAlias
# ours
from .singleton import MetaSingleton


# alias (stringify)
Daemon : TypeAlias = "Daemon"


class Progress(object, metaclass = MetaSingleton):
    """
        A simple throbber/progressbar that runs in another thread
        This is in a separate module because it may not be persisted
        in pycall, and thus is not considered a core part of the module
    """

    enable = False # disabled by default, enabled if could start

    def __init__(self):
        """
            initialize progress singleton properties
        """
        try : 
            from rich.progress import Progress as rp
            self._richprogress = rp(transient=True)
        except ModuleNotFoundError:
            pass  # TODO : add a "default" throbber
        else :
            self._executor = ThreadPoolExecutor(max_workers=1)
            self._dd : dict = {}
            self.enable = True


    def schedule(self, daemon : Daemon) -> None :
        """
            add a daemon to "throb" for 
        """        
        if not self.enable :
            return
        logging.info(f"adding throbber for '{daemon}'")
        tid = _richprogress.add_task(daemon.name, total=None)
        fut = self._executor.submit(asyncio.run, self._display())
        self._dd[daemon] = fut, tid # keeping future for cancellation


    def cancel(self, daemon : Daemon) -> None :
        """ 
            remove one of the daemons from the throbber
            cancel/stop the throbber if no daemons are running
        """
        if not self.enable :
            return
        fut, tid = self._dd.pop(daemon)
        try :
            fut.cancel()
            self._richprogress.stop_task(tid)
        except :
            pass
        finally :
            if len(self._dd) == 0 : 
                self._richprogress.stop()
                


    async def _display(self) :
        """ 
            display a nice throbber/progressbar in the console
        """
        try :
            while True :
                for (daemon,(fut,task_id)) in self._dd.items() :
                    if daemon.progress is not None :
                        if not progress._tasks[task_id].started :
                            progress.start_task(task_id)
                        progress.update(progress_task, completed=daemon.progress, total=1.0)
                logging.debug(f"throbber : progress update : {len(self.__dd)} daemons")
                progress.refresh()
                await asyncio.sleep(1.0/60.0)
        except asyncio.CancelledError : 
            logging.info(f"cancelling throbber")
            return # stop !

