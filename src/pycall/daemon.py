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

Callback = Callable|None


async def _read_stream(stream, cb_list : List[Callback]) -> None :
    """ helper method, used to avoid code duplication between stderr and stdout """
    while True:
        line = await stream.readline()
        if line:
            for cb in cb_list :
                if cb is not None :
                    cb(line.decode(locale.getencoding()))
        else:
            break


class Daemon(object) :
    """
        Class for making exec calls asynchronously
        we do not run in a shell, but the process is executed
        in a separate thread.

        you do not need to interact directly with this class,
        instead use the pycall functions
    """

    def __init__(self, cmd, *, 
            stdout_func : Callback = None,
            stderr_func : Callback = None,
            on_end_func : Callback = None ) :
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


    @classmethod
    def get_runner(cls) -> asyncio.Runner :
        try : 
            return cls._runner
        except AttributeError :
            cls._runner = asyncio.Runner()
            return cls._runner


    @classmethod
    def get_throbber(cls) -> Throbber :
        try : 
            return cls._throbber
        except AttributeError :
            cls._throbber = Throbber()
            return cls._throbber
        

    def execute(self) -> None:
        """ add to the list of coroutines to run """
        runner = type(self).get_runner()
        self._fut = runner.run(self._process())


    def run_until_complete(self) -> Output:
        """ run blocking """
        return asyncio.run(self._process())


    async def task(self) -> asyncio.Task :
        """ run command in a separate task """
        self._fut = asyncio.create_task(self._process())
        return self._fut


    async def _process(self) -> Output :
        """ 
            run the actual process, along with a throbber,
            an output object and some parsing tasks
        """
        self.result = None # out is not a future, it either holds the output or not
        self.get_throbber().schedule()
        out = Output(' '.join(self.args))
        _pipe = asyncio.subprocess.PIPE
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        # regroup tasks
        stdout = asyncio.create_task(_read_stream(ps.stdout, [out.stdout , self.__stdout_f ] ))
        stderr = asyncio.create_task(_read_stream(ps.stderr, [out.stderr , self.__stderr_f ] ))
        fut = asyncio.gather(stdout, stderr)
        # put in a task, to cancel
        print(f"gather in a task")
        tk = asyncio.create_task(ps.wait())
        tk.add_done_callback(fut.cancel)
        tk.add_done_callback(self.__on_complete)
        await tk
        out.close(ps.returncode)
        return out


    def is_running(self) -> bool :
        """ returns true if process is still running """
        return self.result is None
        

    def __on_complete(self, fut : asyncio.Future ) -> None :
        """ 
            retrieve output and call the finished callbacks upon return
        """
        self.get_throbber().cancel()
        self.out = fut.result()
        print("Daemon has completed")
        if self.__cb_f is not None :
            print(f"calling {self.__cb_f}")
            self.__cb_f(self.result)

    def __await__(self) :
        return self._fut

    async def wait(self) :
        if isinstance(self._fut, asyncio.Future) :
            await self._fut


