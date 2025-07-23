#!/usr/bin/env python
# shortcut to avoid multiple imports
# python
import asyncio

# ours
from .daemon import Daemon
from .output import Output


def run(*args, **kwargs) -> Daemon :
    """
        simple call one shell command
    """ 
    return Daemon(*args, **kwargs)
