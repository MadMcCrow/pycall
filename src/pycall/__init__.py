#!/usr/bin/env python
# shortcut to avoid multiple imports
# python
import asyncio

# ours
from .command import Command
from .output import Output


def run(*args, **kwargs) -> Output :
    """
        simple call one shell command
    """ 
    r = Command(*args, **kwargs)
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(r.asyncrun())

async def async_run(*args, **kwargs) -> Output:
    """
        simple async call one shell command
    """ 
    r = Command(*args, **kwargs)
    return await r.asyncrun()

def batch_run(coros : list) : 
    """
        allow running multiple Commands in "parallel"
        (it is not true parallelism, but at least they are concurrent) 
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_batch_run(coros))

async def async_batch_run(coros : list) : 
    """
        allow running multiple Commands in "parallel"
        async version allowing for even more composition !
        (it is not true parallelism, but at least they are concurrent) 
    """
    out = []
    end = lambda fut : out.append(fut.result()) 
    async with asyncio.TaskGroup() as tg:
        for c in coros : 
            r = Command(*c)
            t = tg.create_task(r.asyncrun())
            t.add_done_callback(end)
    return out
