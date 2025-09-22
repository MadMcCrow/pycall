#!/usr/bin/env python
# entrypoint for pycall

# python
import asyncio
from typing import Callable, TypeAlias, Optional
# ours
from .daemon import Daemon
from .queue  import Queue

# alias
Callback : TypeAlias = Optional[Callable]



def init(cmd) -> Daemon :
    """
        Spawns a daemon, ready to run
    """ 
    return Daemon(cmd)

def run(daemon : Daemon) -> None :
    """
        Add a daemon to the queue for execution
    """
    Queue().schedule(daemon) 


def wait( *daemons : Daemon ) :
    """
        wait for multiple daemons to complete
        this will block execution until every daemon passed has completed
    """
    for d in daemons :
        Queue().wait(d)

def waitall() :
    """
        wait for all daemons to complete
        this will block execution until all daemon has completed
    """
    daemons = Daemon._instances
    wait(daemons)