#!/usr/bin/env python

# python
import asyncio
from typing import Callable, List

# ours
from .daemon import Daemon
from .output import Output

# alias
Callback = Callable|None

def run(cmd, *, stderr_f : Callback = None, stdout_f : Callback = None, on_end_f : Callback = None) -> Daemon :
    """
        run a shell or exec in a background thread and either parse its content or just wait for the result
        this call is not blocking and does not require you use asyncio
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    d.execute()
    return d


def run_blocking(cmd, *, stderr_f : Callback = None, stdout_f : Callback = None, on_end_f : Callback = None) -> Output :
    """
        run a shell or exec and wait for the result
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    return d.run_until_complete()


async def run_async(cmd, *, stderr_f : Callback = None, stdout_f : Callback = None, on_end_f : Callback = None) -> asyncio.Task :
    """
        run a shell or exec as a asyncio task 
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    return await d.task()


def wait(*daemons) :
    loop = asyncio.get_event_loop()
    for d in daemons :
        t = asyncio.create_task(d.wait())
        loop.run_until_complete(t)