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
        don't forget to wait on your daemons, because otherwise your program will exit
    """ 
    d = Daemon(cmd, **kwargs)
    d.run()
    return d


def wait(*daemons) :
    """
        wait for multiple daemons to complete
        this will block execution until every daemon passed as completed
    """
    try :
        async def shutdown(daemon) :
            await daemon
        loop = asyncio.get_running_loop()
        with asyncio.TaskGroup() as tg:
            for d in daemons :
                tg.create_task(shutdown(d))
            loop.run_until_complete(tg)
    except RuntimeError : 
        pass
    finally:
        for d in daemons :
            print("d has finished")
        return map(lambda x: x.result, daemons)