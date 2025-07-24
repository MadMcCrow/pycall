#!/usr/bin/env python
# Class to have async calls to programs

# default python modules
from typing import Callable, List
import shutil, shlex
import asyncio
import locale

# ours
from .throbber import Throbber
from .output   import Output

class Daemon() :
    """
        Class for making exec calls asynchronously
        we do not run in a shell, but the process is executed
        in a separate thread.

        you do not need to interact directly with this class,
        instead use the pycall functions
    """

    # class property !
    __runner = asyncio.Runner()

    def __init__(self, cmd, *, 
            stdout_func : Callable = None,
            stderr_func : Callable = None,
            on_end_func : Callable = None ) :
        """ create an run Daemon process """
        # copy arguments :
        self.args = shlex.split(cmd)
        self.__stdout_f = stdout_func
        self.__stderr_f  = stderr_func
        self.__cb_f     = on_end_func
        # initialize result :
        self.result = None
        # check it make sens :
        if shutil.which(self.args[0]) is None:
            raise RuntimeError(f"{self.args[0]} : command not found")

    def execute(self) -> None:
        """ add to the list of coroutines to run """
        runner = type(self)._Daemon__runner
        fut = runner.run(self._process())

    def run_until_complete(self) -> None:
        """ run blocking """
        asyncio.run_until_complete(self._process())


    async def task(self) -> None :
        """ run command in a separate task """
        ps = asyncio.create_task(self._process())



    async def _process(self) -> Output :
        """ 
            run the actual process, along with a throbber,
            an output object and some parsing tasks
        """
        self.result = None # out is not a future, it either holds the output or not
        th = Throbber()
        out = Output(self.args)
        _pipe = asyncio.subprocess.PIPE
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        # regroup tasks
        tl = []
        tl.append(asyncio.create_task(th.display()))
        tl.append(asyncio.create_task(self.__read_stream(ps.stdout, [out.stdout , self.__stdout_f ] )))
        tl.append(asyncio.create_task(self.__read_stream(ps.stderr, [out.stderr , self.__stderr_f ] )))
        fut = await asyncio.gather(*tl)
        # put in a task, to cancel
        print(f"gather in a task")
        tk = await asyncio.create_task(ps.wait())
        tk.add_done_callback(fut.cancel())
        out.close(ps.returncode)
        return out


    def is_running(self) -> bool :
        """ returns true if process is still running """
        return self.result is None
        


    def __on_complete(self, fut : asyncio.Future ) -> None :
        """ 
            retrieve output and call the finished callbacks upon return
        """
        self.out = fut.result()
        print("Daemon has completed")
        if self.__cb_f is not None :
            print(f"calling {self.__cb_f}")
            self.__cb_f(self.result)

    @staticmethod
    async def __read_stream(stream, cb_list : List[Callable]) -> None :
        """ helper method, used to avoid code duplication between stderr and stdout """
        while True:
            line = await stream.readline()
            if line:
                for cb in cb_list :
                    if cb is not None :
                        cb(line.decode(locale.getencoding()))
            else:
                break

