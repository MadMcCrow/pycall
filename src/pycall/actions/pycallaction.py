#!/usr/bin/env python
# Action class for calling a process

# python imports
from typing import (
    List,
    TypeAlias,
    Callable
)
from shutils import which

# ours
from .pyaction import PyAction


_pipe = asyncio.subprocess.PIPE




class PyCmd(object) :
    """
        Class to describe a shell command or a program call with arguments
    """

    def __init__(self, cmd : str, args : List[str] ) :
        self.cmd = cmd
        self.args = args

    def __iter__(self):
        return iter([self.cmd] + self.args)

    @property
    def cmd(self) :
        return self.__cmd

    @cmd.setter
    def cmd(self, cmd : str) :
        if which(cmd) is not None :
            self.__cmd = cmd
        else :
            raise RuntimeError(f"could not find command `{cmd}` in path.")

    @property
    def args(self) :
        return self.__args

    @args.setter
    def args(self, args : List[str]) :
        self.__args = []
        for a in args :
            a = a.strip() # remove whitespaces
            if a.strip(["'", '"']) == a and ' ' in a : # not quoted and contains spaces
                self.__args += a.split(' ')
            else :
                self.__args.append(a)



class PyCallAction(PyAction) :
    """
        Action that calls a command and wait for its completion
    """

    # type aliases for simplicity
    _IOStream : TypeAlias = tuple[str,str]                # as in [stdout, stderr]
    CB_Progress : TypeAlias = Callable[_IOStream, float ] # as in _IOStream -> float
    CB_Stream   : TypeAlias = Callable[_IOStream, None  ] # as in _IOStream -> None


    def __init__(   self,  cmd : PyCmd, *,
                    dependencies : List["PyAction"] = [],                   # as documented in super
                    callbacks : List[(CB_Progress | CB_Stream)]= []) :     # will called when either stdout 
        """
            create an Action with dependencies to do first and a coroutine to execute

            Keyword arguments:
            dependencies -- list of PyAction to execute before this one
            call         -- process to run 
            callbacks    -- functions to call when we receive stdout or stderr
        """
        super().__init__( dependencies = dependencies, coro = self._call, mode = Execution.PROCESS)
        self._cmd = cmd
        self._cbs = callbacks

    
    async def _call(self) :
        """ 
            run the actual process
        """
        # inner function to get from stream to string
        async def read_stream(stream, cb) -> None :
            while True:
                line = await stream.readline()
                logging.debug(f"call '{self.name}' : received {stream} : {line}")
                if line:
                    cb(line.decode(locale.getencoding()))
                else:
                    break
        # start the subprocess
        ps = await asyncio.create_subprocess_exec(self.args[0], *self.args[1:], stdout=_pipe, stderr=_pipe)
        logging.info(f"Daemon '{self}' : started process")
        # regroup parsing task
        stdout = asyncio.create_task(read_stream(self.__stdout))
        stderr = asyncio.create_task(read_stream(self.__stderr))
        fut = asyncio.gather(stdout, stderr)
        # add callbacks
        self._fut  = asyncio.create_task(ps.wait())
        self._fut.add_done_callback(fut.cancel)
        self._fut.add_done_callback(self.__on_complete)
        return self._fut 


    async def __stdout(self, in_str : str) :
        for cb in self.pcbs :
            ret = cb([in_str,None])
            if isinstance(ret,float) :
                self.progress = ret

    async def __stdout(self, in_str : str) :
        for cb in self.pcbs :
            ret = cb([None,in_str])
            if isinstance(ret,float) :
                self.progress = ret

        