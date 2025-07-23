#!/usr/bin/env python
# class to store the output from a command

# python
from datetime import datetime
import asyncio

# ours
from .exception import PycallException

# private wrapper function 
def _time() :
    return datetime.now()

class Output() :

    __out = {}          # output
    __err = {}          # errors
    __rc = None         # return code
    __end = None        # end time

    def __init__(self, args : str, name = None) -> None:
        self.name = name
        self.__cmd = ' '.join(args)
        self.__start = _time()


    def stdout(self, instr : str) -> None :
        if self.is_closed() :
            raise RuntimeError("trying to add stdout to closed output")
        self.__out[_time()] = instr

    def stderr(self, instr : str) -> None :
        if self.is_closed() :
            raise RuntimeError("trying to add error to closed output")
        self.__err[_time()] = instr


    def __str__(self) -> str:
        if self.__end is None :
            raise PycallException("parsing incomplete output may lead to issues !")
        res = ""
        for (k,v) in self.__out.items() :
            res += v + '\n'
        return res

    def is_closed() -> bool : 
        """ return true if this output is read-only"""
        return self.__end is not None

    def log(self) -> str :
        """ write as a log """
        l = []
        for (k,v) in self.__out.items() :
            l.append(f'<{k}> - {v}')
        for (k,v) in self.__err.items() :
            l.append(f'<{k}> - ERROR : {v}')
        l.sort()
        l.insert(0, f"'{self.__cmd}' started at {self.__start}")
        l.append(f'execution took {self.duration()}')
        return '\n'.join(l)


    def close(self, fut : asyncio.Future) -> None :
        """
        close this output
        """
        self.__end = _time()
        self.__rc = fut.result()

    def duration(self) -> float :
        """
        get execution duration in seconds
        """
        if self.__end is not None :
            return self.__end - self.__start 
        return (_time() - self.__start).total_seconds