from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import argparse
import time

from lib import logger


class Command(object):
    def __init__(self, allow_unknown_args=False, add_arg_help=True):
        self.parser = argparse.ArgumentParser(prog='Master Builder',
                                              description='Build System for containers',
                                              add_help=add_arg_help)
        self.parser.add_argument('--verbose',
                                 action='store_true',
                                 help='Enables Verbose output for build command')
        self.log = logger.get_logger('[{0}]'.format(self.__class__.__name__))
        self.log.debug('Initializing {0}'.format(self.__class__.__name__))
        self.allow_unknown_args = allow_unknown_args

    def wrapped_run(self, arguments):
        unknown_args = None
        if self.allow_unknown_args:
            parsed_args, unknown_args = self.parser.parse_known_args()
        else:
            parsed_args = self.parser.parse_args(arguments)

        start = time.time()
        return_value = self.run(parsed_args, unknown_args, arguments)
        end = time.time()
        self.log.info('Command Time: {0}'.format(end - start))

        return return_value

    @abc.abstractmethod
    def run(self, parsed_args, unknown_args, original_arguments):
        raise NotImplementedError("'_run' must be reimplemented by %s" % self)


class DemoCommand(Command):
    def run(self, parsed_args, unknown_args, original_arguments):
        self.log.info("Demo Command...")
