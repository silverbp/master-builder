from __future__ import absolute_import
from __future__ import unicode_literals

import inspect
import logging
import traceback

__m = {}
__m['log_level'] = logging.INFO


def set_log_level(level):
    __m['log_level'] = getattr(logging, level, logging.INFO)


def printinfo():
    frame = inspect.currentframe()
    stack_trace = traceback.format_stack(frame)
    print(stack_trace[:-1])


def get_logger(name):
    if name in __m:
        return __m[name]

    logger = logging.getLogger(name)
    logger.setLevel(__m['log_level'])
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    __m[name] = logger
    return logger
