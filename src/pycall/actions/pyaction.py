#!/usr/bin/env python
# Base Action class


# python imports
from asyncio import (
    create_task
    gather
)

from typing import (
    Optional,
    List,
    Coroutine
)

from logging import (
    error,
    info,
    debug
)

from enum import Enum


class PyAction(object) :
    """
        Class for doing things asynchronously.
        this makes making an async program really easy.
        they are called actions to avoid conflicting with "tasks".
    """

    class Status(Enum) :
        """
            Describe action status with an enum
        """
        READY   = 0
        STARTED = 1
        DONE    = 2


    class Execution(Enum) :
        """
            How to run the action :
            ASYNC   -- as a asyncio task (default)
            THREAD  -- as a Thread in a thread pool   (io_bound)
            PROCESS -- as a Process in a process pool (cpu_bound)
        """
        ASYNC   = 0
        THREAD  = 1
        PROCESS = 2


    def __init__( self, *, dependencies = List["PyAction"], coro : Optional[Coroutine] = None, mode = Execution.ASYNC, Callback :Optional [P] ) :
        """
            create an Action with dependencies to do first and a coroutine to execute

            Keyword arguments:
            dependencies -- list of PyAction to execute before this one
            coro         -- the coroutine to execute once dependencies are done
        """
        self._status = Status.READY
        self._deps = dependencies
        self._coro = coro
        self._para = mode
        self._prog = None


    def is_done(self) -> bool :
        return self._status == DONE
    
    
    async def start(self) :
        """
            run all dependencies and then do our task
        """
        if self._status != Status.READY :
            info(f"tried to start <{repr(self)}>, but is already <{self._status}>")
            return
        self._status = Status.STARTED
        await self.wait_for_deps()
        # now our turn :
        if self._coro is not None :
            selftask = asyncio.create_task(self._coro)        
            await selftask
        
        self._status = Status.DONE


    async def wait_for_deps(self) :
        """
            awaitable coroutine to make sure all dependencies are complete before 
        """
        loop = asyncio.get_running_loop() # a loop should be active right now !
        async def group_deps() : 
            async with asyncio.TaskGroup() as tg:
                for d in self._deps :
                    if not d._started :
                        tg.create_task(d._start)
        # execute with mode in mind
        await self._execute(group_deps, self._para)


    @property
    def progress(self) -> Optional[float] :
        """
            return how much as been done
        """
        try :
            if self._coro is None : 
                done = float(len([x for x in self._deps if x.is_done()])) 
                total = float(len(self._deps))
                return done / total
            else : 
                return self._prog # you need to report what you done yourself
        except :
            return None

    @progress.setter
    def progress(self, value : Optional[float]) :
            self._prog = value


    def on_complete(self) :
        pass

    @static_method
    async def _execute(coro, mode) :
        """
            helper function to run a coroutine in different modes :
        """
        match self._para :
            case Execution.ASYNC :
                await coro()
            case Execution.THREAD :
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    await loop.run_in_executor(pool, coro)
            case Execution.PROCESS :
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    await loop.run_in_executor(pool, coro)


def start(action : PyAction) :
        """
            will start this action, begining by the dependencies
            arguments :
            action -- a corectly initialized action that you want to start.
        """
        # sanity check : verify it may complete before starting the async progress 
        all_deps = {}
        temp = action._deps
        while len(temp) > 0 :
            d = temp.pop(0)
            all_deps.append(d)
            temp += d._deps
        nodeps = [ x for x in all_deps if len(x._deps) == 0 ]
        if len(nodeps) == 0 :
            raise RuntimeError(f"PyAction <{repr(action)}> has looping dependencies")
        # schedule this action
        asyncio.run(action.start)