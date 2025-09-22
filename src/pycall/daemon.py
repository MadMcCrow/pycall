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
from .progress import Progress


# aliases :
StreamCallback : TypeAlias = Optional[Callable[[str],None]]

# ideally we would make a better type that can automatically select the correct type
# adding '| None' for the static type checker (and because it's simpler than Optional)
# we coud stringify annotation to avoid looping references :
# from __future__ import annotations
ReturnCallback : TypeAlias = Callable[[int],None]
DaemonCallback : TypeAlias = Callable[["Daemon"],None] # stringified : not implemented yet
EndCallback : TypeAlias  = DaemonCallback | ReturnCallback | None 


class Daemon(object) :
    """
        Class for making exec calls asynchronously
        we do not run in a shell, but the process is executed
        in a separate thread.

        you do not need to interact directly with this class,
        instead use the pycall functions
    """
    
    def call_on_end(self, cb : ReturnCallback):
        """
            add a callback for the end or call directly
        """
        if self.is_running() :
            self._end_cb.append(cb)
        else :
            cb(self._fut())

    def call_on_stdout(self, cb : ReturnCallback):
        """
            add a callback for the stdout or call directly
        """
        if self.is_running() :
            self._stdout_cb.append(cb)
        else :
            cb(self._out)


    def call_on_stderr(self, cb : ReturnCallback):
        """
            add a callback for the stdout or call directly
        """
        if self.is_running() :
            self._stdout_cb.append(cb)
        else :
            cb(self._err)

    
    def __init__(self, cmd) :
        """
            initialize every variable :
        """ 
        # name and command 
        self.__set_cmd(cmd)
        self.__set_name()
        # output
        self._out = ""
        self._err = ""
        # callbacks :
        self._end_cb = []
        self._stdout_cb = []
        self._stderr_cb = []
        # future is None (not yet started)
        self._fut = None


    async def _process(self) -> None :
        """ 
            run the actual process, along with a throbber (progress),
            an output object and some parsing tasks
        """
        # inner function to get from stream to string
        async def read_stream(stream, cb) -> None :
            while True:
                line = await stream.readline()
                logging.debug(f"Daemon '{self.name}' : received {stream} : {line}")
                if line:
                    cb(line.decode(locale.getencoding()))
                else:
                    break
        # start the subprocess
        _pipe = asyncio.subprocess.PIPE
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        logging.info(f"Daemon '{self}' : started process")
        # starting the progressbar
        Progress().schedule(self)
        # regroup parsing task
        stdout = asyncio.create_task(read_stream(ps.stdout, self.__stdout))
        stderr = asyncio.create_task(read_stream(ps.stderr, self.__stderr))
        fut = asyncio.gather(stdout, stderr)
        # add callbacks
        self._fut  = asyncio.create_task(ps.wait())
        self._fut.add_done_callback(fut.cancel)
        self._fut.add_done_callback(self.__on_complete)
        return self._fut 

    def __stdout(self, stream) :
        self._out += stream
        logging.debug(f"{self.name} # STDOUT : {stream}")
        for cb in self._stderr_cb :
            cb(stream)

    def __stderr(self, stream) :
        self._out += stream
        logging.warning(f"{self.name} # STDERR : {stream}")
        for cb in self._stdout_cb :
            cb(stream)

    def __on_complete(self, fut : asyncio.Future ) -> None :
        """ 
            retrieve returncode and call the finished callbacks upon return
        """
        logging.info(f"Daemon '{self.name}' : completed")
        Progress().cancel(self)
        if self.__cb_f is not None :
            sig = signature(self.__cb_f)
            if len(sig.parameters) == 0 :
                self.__cb_f_()
            elif len(sig.parameters) > 1 :
                raise TypeError("'on_end_func' expects a function with one or zero parameter")
            else :
                paramtype = list(sig.parameters.values())[0].annotation
                if paramtype is int : 
                    self.__cb_f(self.return_code())
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
        try :
            return self._fut
        except :
            return None


    def is_running(self) -> bool :
        """
            return true if the process is still running
        """
        try :
            return not self._fut.done()
        except : 
            return True


    def return_code(self) -> Optional[int]:
        """
            get result of the execution
        """
        if self._fut is not None :
            if self._fut.done() : 
                return self._fut()
        return None


    def __set_name(self) :
        """
            make sure the daemon has a unique name
        """
        global names
        name = self.args[0]
        try :
            idx = 0
            while name in names :
                name = f"{name}-{idx}"
                idx += 1
        except :
            names = []
        finally :
            names.append(name)
            self.name = name


    def __set_cmd(self, cmd) :
        args = shlex.split(cmd)
        if shutil.which(args[0]) is None:
            raise RuntimeError(f"{args[0]} : command not found")
        self.args = args

    def __str__(self) :
        return self.name