#!/usr/bin/env python
# Class to provide storage and function to allow multiple calls to run either async or in serie

# python
import asyncio
from .singleton import MetaSingleton
from concurrent.futures import ThreadPoolExecutor
import logging

# ours
from .daemon import Daemon

class Queue(object, metaclass = MetaSingleton):
    """
        Keep track of started daemons 
        make sure to execute them all
    """

    _daemons = [] 


    def __init__(self) :
        self._executor = ThreadPoolExecutor(max_workers=10)


    def schedule(self, d : Daemon) :
        """
            run in a backround thread
        """
        self._daemons.append(d)
        future = self._executor.submit(asyncio.run, d._process())


    async def _await_daemon(self, d : Daemon) :
        """
            async await daemon
        """
        return await daemon


    def wait(self, d : Daemon ) :
        """
            wait for a daemon completion (blocking)
        """
        try :
            loop = asyncio.get_event_loop()
            with asyncio.TaskGroup() as tg:
                tg.create_task(self._await_daemon(d))
                loop.run_until_complete(tg)
        except RuntimeError as E : 
            logging.error(f"Runtime Error when waiting for {d} : {E}")
            pass
        finally:
            logging.info(f"{d} has completed")
            return d.return_code()