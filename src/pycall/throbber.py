#!/usr/bin/env python
# Class to display a simple throbber

import asyncio
import time
from concurrent import futures





class Throbber() :
    """
    A simple throbber that runs in another thread
    """
    def __init__(self) -> None:
        self.__idx = 0
        self._fut = asyncio.create_task(self.__update())

    def cancel(self, fut) :
        self._fut.cancel()

    async def __run(self):
        await loop.run_in_executor(None, __update())

    async def __update(self) :
        # settings :
        __characters = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        __len = len(__characters)
        __wait = 0.1
        # loop :
        while True :
            self.__idx = (self.__idx + 1) % __len
            print(__characters[self.__idx], end='\r')
            #time.sleep(__wait)
            await asyncio.sleep(__wait)

