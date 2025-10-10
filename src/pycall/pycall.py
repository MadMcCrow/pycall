#!/usr/bin/env python
# Class to have async calls to programs
# The Core of pycall

 

from shutil import which

# asyncio deps
from asyncio import (
    TaskGroup,
    create_task,
    gather,
    subprocess,
    create_subprocess_exec
)

# typing
from typing import (
    List,
 )

# ours
from .output import Callback, Output

class Pycall(object) :
    """
        Class for making exec calls asynchronously
        we do not run in a shell, but the process is executed
        in a separate thread.

        you do not need to interact directly with this class,
        instead use the pycall functions
    """

    @classmethod
    async def call( cls, cmd : str, args : List[str], * cbs : Callback ):
        """ 
            create an run Pycall process.

        """
        self : Pycall = cls()
        self.__private_init(cmd, args, list(*cbs))
        await self.__process()
        return self


    async def __process(self) -> None :
        """ 
            run the actual process, along with a throbber,
            an output object and some parsing tasks
        """
        # create process :
        ps = await create_subprocess_exec(self.__cmd, *self.__args, 
                                            stdout= subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        async with TaskGroup() as tg :
            tg.create_task(ps.wait())
            tg.create_task(self.__out.parse_stdio(ps))



    def __await__(self) :
        return self.__task.__await__()

    def __private_init(self, cmd, args, cbs ) :
        """
            initialize this Pycall object with what's
        """
        if which(cmd) is None:
            raise RuntimeError(f"{cmd} : command not found")
        self.__cmd = cmd
        self.__out = Output(cbs)
        # TODO : perform checks on args :
        self.__args = args
        # init output :
        self.__task = create_task(self.__process())


    def rc(self) :
        return self.__out.return_code()


    def stdout(self) -> str :
        return self.__out._out


    def stderr(self) -> str :
        return self.__out._err