#!/usr/bin/env python
# Class to display a simple throbber

import asyncio
import time
from concurrent import futures


try : 
    from rich.progress import Progress 
    _enable_throbber = True
    progress = Progress(transient=True)
except ModuleNotFoundError:
    pass

class Throbber() :
    """
        A simple throbber/progressbar that runs in another thread
        This is in a separate module because it may not be persisted
        in pycall, and thus is not considered a core part of the module
    """

    _dd : dict = {}


    def schedule(self, daemon : "Daemon") -> None :
        """
            add a daemon to "throb" for 
        """
        try : 
            _enable_throbber and self._fut.done()
        except  NameError :
            return
        except AttributeError :
            self._fut = asyncio.create_task(self._display())
            progress.start()
        finally :
            self._dd[daemon] = progress.add_task(daemon.name, total=None)


    def cancel(self, daemon : "Daemon") -> None :
        """ 
            remove one of the daemons from the throbber
            cancel/stop the throbber if no daemons are running
        """
        try : 
            progress.stop_task(self._dd.pop(daemon))
        finally :
            if len(self._dd) <= 0:
                self._fut.cancel()
                self._fut = None
                progress.stop()


    async def _display(self) :
        """ display a nice throbber in the console """
        try :
            while True :
                for (daemon,task_id) in self._dd.items() :
                    if daemon.progress is not None :
                        if not progress._tasks[task_id].started :
                            progress.start_task(task_id)
                        progress.update(progress_task, completed=daemon.progress)
                progress.refresh()
                await asyncio.sleep(1.0/60.0)
        except asyncio.CancelledError : 
            return # stop !

