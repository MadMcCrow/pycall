#!/usr/bin/env python
# output / logging support

from asyncio import (
    TaskGroup,
    subprocess,
)

from typing import (
    List,
    Callable,
    TypeAlias,
    Optional
)

from logging import (
    error,
    debug
)

from locale import getencoding

# output callback type alias
Callback : TypeAlias = Callable[[str,bool],Optional[float]]

class Output(object) :
    """
        support class to write output and log.
        this is not exposed to the user, but it implements the methods
        used in the class Pycall
    """

    def __init__(self, cbs: List[Callback] = []) :
        self._out = ""
        self._err = ""
        self._cbs = cbs
        self._prg = None
        self._rc  = None

    async def parse_stdio(self, ps : subprocess.Process ) :
        debug(f"starting output object for process {ps}")
        async with TaskGroup() as stdio_tasks :
            stdio_tasks.create_task(self._read_stream(ps.stdout, False ))
            stdio_tasks.create_task(self._read_stream(ps.stderr, True ))
        self._rc = ps.returncode

    async def _read_stream(self, stream, err : bool = False) -> None :
        """
            helper method to parse stdout and stderr the same way
        """
        while True:
            line = await stream.readline()
            if line:
                txt = line.decode(getencoding())
                if err :
                    self._err += f"\n{txt}"
                else :
                    self._out += f"\n{txt}"
                for cb in self._cbs :
                    try :
                        res = cb(txt, err)
                        if isinstance(res, float) :
                            self._prg = res
                    except Exception as E :
                        error(f"{type(E)} : failed to call {cb} : {E}")
                        continue # ignore problem
            else:
                break

    def cancel(self) :
        pass

    def progress(self) -> Optional[float] :
        return self._prg

    def return_code(self) -> Optional[int] :
        return self._rc
   