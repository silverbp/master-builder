from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import argparse
import time

from mb.lib import logger


class Command(object):
    def __init__(self, allow_unknown_args=False, add_arg_help=True, description="command"):
        self.parser = argparse.ArgumentParser(prog=self.__class__.__name__,
                                              description=description,
                                              add_help=add_arg_help)
        self.parser.add_argument('--verbose',
                                 action='store_true',
                                 help='Enables Verbose output')
        self.log = logger.get_logger('[{0}]'.format(self.__class__.__name__))
        self.log.debug('Initializing {0}'.format(self.__class__.__name__))
        self.allow_unknown_args = allow_unknown_args
        self.dependencies = ['_prerun']

    def run(self, arguments):
        unknown_args = None
        if self.allow_unknown_args:
            parsed_args, unknown_args = self.parser.parse_known_args()
        else:
            parsed_args = self.parser.parse_args(arguments)

        start = time.time()
        return_value = self._run(parsed_args, unknown_args, arguments)
        end = time.time()
        self.log.info('Command Time: {0}'.format(end - start))

        return return_value

    @abc.abstractmethod
    def _run(self, parsed_args, unknown_args, original_arguments):
        raise NotImplementedError("'_run' must be reimplemented by %s" % self)


class MBPreRunCommand(Command):
    def __init__(self, template_engine, version_scheme, build_context):
        super(MBPreRunCommand, self).__init__(add_arg_help=False)
        # self.dependencies = []
        self._template_engine = template_engine
        self._version_scheme = version_scheme
        self._build_context = build_context

    def _run(self, parsed_args, unknown_args, original_arguments):
        version = self._version_scheme.generate()
        self._build_context.add_variables(version)
        self._template_engine.generate_files()


class DemoCommand(Command):
    def __init__(self):
        super(DemoCommand, self).__init__()
        self._test_property = "initial"

    def _run(self, parsed_args, unknown_args, original_arguments):
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


class ShellCommand(Command):
    pass
