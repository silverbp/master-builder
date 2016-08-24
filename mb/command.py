from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import argparse
import time

from mb.lib import logger


class Command(object):
    def __init__(self, allow_unknown_args=False, add_arg_help=True, description="command"):
        self.parser = argparse.ArgumentParser(prog='mb',
                                              description=description,
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
        raise NotImplementedError("'run' must be reimplemented by %s" % self)


class DemoCommand(Command):
    def __init__(self):
        super(DemoCommand, self).__init__()
        self._test_property = "initial"

    def run(self, parsed_args, unknown_args, original_arguments):
        self.log.info("Demo Command...")
        self.log.info("Test Property: " + self._test_property)

    @property
    def test_property(self):
        return self._test_property

    @test_property.setter
    def test_property(self, value):
        self._test_property = value


class DockerCommand(Command):
    pass
