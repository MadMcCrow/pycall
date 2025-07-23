#!/usr/bin/env python
# Class to have async calls to programs

# default python modules
from typing import Callable
from datetime import datetime
import shutil, shlex
import asyncio
import locale



# ours
from .callback import Callback
from .throbber import Throbber
from .output   import Output


class Daemon() :
    """
    Class for making shell calls asynchronously
    """

    args : list
    __callback : Callback
    __errcallback : Callback

    def __init__(self, cmd, name = None, out_func = None, err_func = None ) :
        # copy arguments :
        self.args = shlex.split(cmd)
        self.__callback = Callback(out_func)
        self.__errcallback = Callback(err_func)
        self.__name = None if name is None else str(name)
        # check it make sens :
        if shutil.which(self.args[0]) is None:
            raise RuntimeError(f"{self.args[0]} : command not found")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(self._asyncrun)

    def is_running(self) -> bool :
        """
            returns true if process is still running
        """
        return self.ps.returncode is None

    async def _asyncrun(self) -> None :
        """
            run command in a separate task/process
        """
        th = Throbber()
        self._out = Output(self.args, self.__name)
        ps = asyncio.create_task(self.__process())
        ps.add_done_callback(th.cancel)
        ps.add_done_callback(self._out.close)

    async def __process(self) -> int :
        """ run the actual process """
        _pipe = asyncio.subprocess.PIPE
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.__read_stream(ps.stdout, [self._out.stdout , self.__callback] ))
            tg.create_task(self.__read_stream(ps.stderr, [self._out.stderr , self.__errcallback ]))
        return await ps.wait()

    async def __read_stream(self, stream, cb_list):
        while True:
            line = await stream.readline()
            if line:
                for cb in cb_list :
                    cb(line.decode(locale.getencoding()))
            else:
                break