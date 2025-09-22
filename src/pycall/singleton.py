#!/usr/bin/env python
# simple singleton reusable meta

class MetaSingleton(type):
    instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None :
            cls.instance = super().__call__(*args, **kw)
        return cls.instance
        
