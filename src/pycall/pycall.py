#!/usr/bin/env python

# python
import shlex
import asyncio
from typing import Callable

# ours
from .daemon import Daemon



def run(cmd, *, stderr_f : Callable = None, stdout_f : Callable = None, on_end_f : Callable = None) -> None :
    """
        run a shell or exec in a background thread and either parse its content or just wait for the result
        this call is not blocking and does not require you use asyncio
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    d.execute()


def run_blocking(cmd, *, stderr_f : Callable = None, stdout_f : Callable = None, on_end_f : Callable = None) -> None :
    """
        run a shell or exec and wait for the result
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    d.run_until_complete()


async def run_async(cmd, *, stderr_f : Callable = None, stdout_f : Callable = None, on_end_f : Callable = None) -> None :
    """
        run a shell or exec as a asyncio task 
    """ 
    d = Daemon(cmd, stdout_func=stdout_f, stderr_func=stderr_f, on_end_func=on_end_f)
    await d.task()