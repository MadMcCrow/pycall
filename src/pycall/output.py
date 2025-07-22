#!/usr/bin/env python
# class to store the output from a command

from datetime import datetime
from .exception import PycallException

def _time() :
    return datetime.now()

class Output() :

    def __init__(self, args : str, name = None) -> None:
        self.name = name
        self.__cmd = ' '.join(args)
        self.__start = _time()
        self.__end = None
        self.__out = {}
        self.__err = {}

    def stdout(self, instr : str) -> None :
        self.__out[_time()] = instr

    def stderr(self, instr : str) -> None :
        self.__err[_time()] = instr


    def __str__(self) -> str:
        if self.__end is None :
            raise PycallException("parsing incomplete output may lead to issues !")
        res = ""
        for (k,v) in self.__out.items() :
            res += v + '\n'
        return res

    def log(self) -> str :
        """
            write as a log
        """
        l = []
        for (k,v) in self.__out.items() :
            l.append(f'<{k}> - {v}')
        for (k,v) in self.__err.items() :
            l.append(f'<{k}> - ERROR : {v}')
        l.sort()
        l.insert(0, f"'{self.__cmd}' started at {self.__start}")
        l.append(f'execution took {self.duration()}')
        return '\n'.join(l)


    def close(self, fut) :
        self.__end = _time()

    def duration(self) :
        if self.__end is not None :
            return self.__end - self.__start 
        return _time() - self.__start