from __future__ import absolute_import
from __future__ import unicode_literals

import inspect

_cache = {}


def memoize(*args, **kw):
    def _memoize(func):
        def wrapper(*args, **kw):
            if len(restrict_args) > 0:
                position_args = [ind for ind, arg in enumerate(inspect.getargspec(func)[0])
                                 if arg in restrict_args]
                hashed_args = tuple(args[i] for i in position_args)
            else:
                hashed_args = args

            key = (func, hashed_args, frozenset(kw.items()))
            try:
                res = _cache[key]
            except KeyError:
                res = _cache[key] = func(*args, **kw)
            return res
        return wrapper

    if len(args) == 1 and callable(args[0]):
        # No arguments, this is the decorator
        restrict_args = []
        return _memoize(args[0])
    else:
        # This is just returning the decorator
        restrict_args = args
        return _memoize
