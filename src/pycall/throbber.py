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
        """ initialize with an index """
        self.__idx = 0
    
    def schedule(self) -> None :
        self._fut = asyncio.create_task(self.display())

    def cancel(self) -> None :
        """ cancel/stop the throbber """
        self._fut.cancel()

    async def display(self) :
        """ display a nice throbber in the console """
        # settings :
        # TODO allow modifying this from pycall functions
        __characters = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        __len = len(__characters)
        __wait = 0.1
        # endless loop :
        while True :
            self.__idx = (self.__idx + 1) % __len
            print(__characters[self.__idx], end='\r')
            #time.sleep(__wait)
            await asyncio.sleep(__wait)

