#!/usr/bin/env python
# class to store the output from a command

# python
from datetime import datetime, timedelta
from typing import Optional

# rich printing
try : 
    from rich import Console
    from rich.theme import Theme
    _console = rich.Console(theme = Theme({
        "date": "dim gray",
        "info": "dim cyan",
        "warning": "yellow",
        "error": "red",
    }))
except :
    pass

class Output() :
        """
            Output of a "Daemon" call
            TODO : rework to simplify and make it core
        """
        
        __out = {}          # output
        __err = {}          # errors
        __rc = None         # return code
        __end = None        # end time

        def __init__(self, args : str) -> None:
            self.__cmd = args
            self.__start = self._time()


        def stdout(self, instr : str) -> None :
            if self.is_closed() :
                raise RuntimeError("trying to add stdout to closed output")
            self.__out[self._time()] = instr


        def stderr(self, instr : str) -> None :
            if self.is_closed() :
                raise RuntimeError("trying to add error to closed output")
            self.__err[self._time()] = instr


        def __str__(self) -> str:
            if self.__end is None :
                raise RuntimeError("parsing incomplete output may lead to issues !")
            res = ""
            for (k,v) in self.__out.items() :
                res += v + '\n'
            return res


        def is_closed(self) -> bool : 
            """ 
                return true if this output is read-only
            """
            return self.__end is not None


        def log(self, *, file : Optional = None) -> None :
            """
                print log, either with fancy colors or not 
            """
            try :
                _console.log(f"[info]{self.__cmd}[\info] started at [date]{self.__start}[\date]")
                outlog = self.__out.items() 
                for (k,v) in self.__err.items() :
                    outlog.append(k,f"[error]{v}[\error]")
                for (k,v) in outlog.items() :    
                    _console.log(f"[date]<{k}>[\date]:{v}")
                _console.log(f"execution took [date]{self.duration()}[\date]")
            except NameError :
                # default to standard python print :
                l = []
                for (k,v) in self.__out.items() :
                    l.append(f'<{k}> - {v}')
                for (k,v) in self.__err.items() :
                    l.append(f'<{k}> - ERROR : {v}')
                l.sort()
                l.insert(0, f"'{self.__cmd}' started at {self.__start}")
                l.append(f'execution took {self.duration()}')
                l = [x.strip('\n') for x in l]
                print('\n'.join(l), file)


        def close(self, result) -> None :
            """
            close this output
            """
            self.__end = self._time()
            self.__rc = result


        def duration(self) -> timedelta :
            """
            get execution duration in seconds
            """
            if self.__end is not None :
                return self.__end - self.__start 
            return (self._time() - self.__start)

        def return_code(self) -> int :
            if self.__rc is None :
                raise RuntimeError(f"called 'return_code' for '{self.__cmd}' before it completed ")

        @staticmethod
        def _time() :
            return datetime.now()
