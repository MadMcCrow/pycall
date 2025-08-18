#!/usr/bin/env python

# python
import asyncio
from typing import Callable, TypeAlias, Optional
# ours
from .daemon import Daemon
from .output import Output

# alias
Callback : TypeAlias = Optional[Callable]

def run(cmd, **kwargs) -> Daemon :
    """
        run a shell or exec in a background thread and either parse its content or just wait for the result
        this call is not blocking and does not require you use asyncio
    """ 
    d = Daemon(cmd, **kwargs)
    d.execute()
    return d


def run_blocking(cmd, **kwargs) -> Output :
    """
        run a shell or exec and wait for the result
    """ 
    d = Daemon(cmd, **kwargs)
    return d.run_until_complete()


async def run_async(cmd, **kwargs) -> asyncio.Task :
    """
        run a shell or exec as a asyncio task 
    """ 
    d = Daemon(cmd, **kwargs)
    return await d.task()


def wait(*daemons) :
    """
        wait for multiple daemons to complete
        this is blocking so use carefully
    """
    try :
        loop = asyncio.get_running_loop()
        for d in daemons :
            t = asyncio.create_task(d.wait())
            loop.run_until_complete(t)
    except RuntimeError : 
        pass
    finally:
        return map(lambda x: x.result, daemons)