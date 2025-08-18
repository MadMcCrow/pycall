#!/usr/bin/env python
# Class to have async calls to programs
# The Core of pycall

# default python modules
import shutil, shlex
import asyncio
from typing import TypeAlias, TypeVar, Optional
from collections.abc import Callable
from inspect import signature
import locale
from datetime import datetime
import logging

# ours
from .throbber import Throbber
from  .output  import Output


# aliases :
# 
StreamCallback : TypeAlias = Optional[Callable[[str],None]]
# ideally we would make a better type that can automatically select the correct type
# adding '| None' for the static type checker (and because it's simpler than Optional)
# we coud stringify annotation to avoid looping references :
# from __future__ import annotations
ReturnCallback : TypeAlias = Callable[[int],None]
DaemonCallback : TypeAlias = Callable[["Daemon"],None] # stringified : not implemented yet
OutputCallback : TypeAlias = Callable[[Output],None]
EndCallback : TypeAlias  = DaemonCallback | OutputCallback | ReturnCallback | None 


class Daemon(object) :
    """
        Class for making exec calls asynchronously
        we do not run in a shell, but the process is executed
        in a separate thread.

        you do not need to interact directly with this class,
        instead use the pycall functions
    """

    def __init__(self, cmd, *, 
            stdout_func : StreamCallback = None,
            stderr_func : StreamCallback = None,
            on_end_func : EndCallback = None,
            enable_throbber : bool = True, 
            name : Optional[str] = None) :
        """ create an run Daemon process """
        # copy arguments :
        self.args = shlex.split(cmd)
        self.name = name if name is not None else cmd
        self.__stdout_f = stdout_func
        self.__stderr_f  = stderr_func
        self.__cb_f     = on_end_func
        self.__thr = enable_throbber
        self.__p = None
        # maybe this needs to be reworked ?
        self.out = Output(' '.join(self.args))
        # check it make sens :
        if shutil.which(self.args[0]) is None:
            raise RuntimeError(f"{self.args[0]} : command not found")
        # create pre-existing future
        self._fut = asyncio.Future()


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
        

    def execute(self) -> Output :
        """ 
            Entry Point :
            runs through a asyncio Runner
        """
        runner = type(self).get_runner()
        self._fut = runner.run(self._process())
        return self._fut

    async def task(self) -> asyncio.Task :
        """ 
            Entry Point :
             run command in a separate task
        """
        self._fut = asyncio.create_task(self._process())
        return self._fut


    async def _process(self) -> None :
        """ 
            run the actual process, along with a throbber,
            an output object and some parsing tasks
        """
        async def read_stream(stream, *cb_list) -> None :
            while True:
                line = await stream.readline()
                if line:
                    [cb(line.decode(locale.getencoding())) for cb in cb_list if cb is not None ]
                else:
                    break
        if self.__thr :
            self.get_throbber().schedule(self)  
        _pipe = asyncio.subprocess.PIPE
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        logging.info(f"Daemon '{self.name}' : started process")
        # regroup tasks
        stdout = asyncio.create_task(read_stream(ps.stdout, self.out.stdout , self.__stdout_f ))
        stderr = asyncio.create_task(read_stream(ps.stderr, self.out.stderr , self.__stderr_f ))
        fut = asyncio.gather(stdout, stderr)
        # put in a task, to cancel
        tk = asyncio.create_task(ps.wait())
        tk.add_done_callback(fut.cancel)
        tk.add_done_callback(self.__on_complete)
        await tk
        

    def __on_complete(self, fut : asyncio.Future ) -> None :
        """ 
            retrieve output and call the finished callbacks upon return
        """
        logging.info(f"Daemon '{self.name}' : completed")
        self.out.close(fut.result())
        self.get_throbber().cancel(self)
        if self.__cb_f is not None :
            sig = signature(self.__cb_f)
            if len(sig.parameters) == 0 :
                self.__cb_f_()
            elif len(sig.parameters) > 1 :
                raise TypeError("'on_end_func' expects a function with one or zero parameter")
            else :
                paramtype = list(sig.parameters.values())[0].annotation
                if paramtype is int : 
                    self.__cb_f(self.out.return_code())
                elif paramtype is Output :
                    self.__cb_f(self.out)
                elif paramtype is type(self) :
                    self.__cb_f(self)
                else : 
                    # default to Daemon
                    self.__cb_f(self)


    @property
    def progress(self) -> Optional[float] :
        """
            progress property can be set by the user
            by default there's no progress
        """
        try : 
            if self._fut.done() : 
                return 1.0
        except :
            pass
        finally :
            return self.__p
    
    @progress.setter
    def progress(self, percent : float) -> None :
        self.__p  = percent
        logging.info(f"Daemon '{self.name}' : progress set to {self.__p}")
    

    def __await__(self) :
        return self._fut


    async def wait(self) :
        if isinstance(self._fut, asyncio.Future) :
            await self._fut


    def is_running(self) -> bool :
        return not self._fut.done()


    def output(self) -> Output: 
        return self.out


    def rc(self) -> int: 
          return self.out.return_code()