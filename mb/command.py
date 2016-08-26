from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import argparse
import subprocess
import time

from mb.lib import logger


class ProcessError(Exception):
    def __init__(self, command, exitCode, output=''):
        self.message = output
        self.command = command
        self.exitCode = exitCode

    def __str__(self):
        return repr(self.exitCode)


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


class ShellCommand(Command):
    def __init__(self, config):
        super(ShellCommand, self).__init__()
        self._cwd = config.project_dir
        self._return_output = True
        self._throw_on_failure = True
        self._expected_exit_code = 0
        self._command = "echo ShellCommand"

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, value):
        self._cwd = value

    @property
    def return_output(self):
        return self._return_output

    @return_output.setter
    def return_output(self, value):
        self._return_output = value

    @property
    def throw_on_failure(self):
        return self._throw_on_failure

    @throw_on_failure.setter
    def throw_on_failure(self, value):
        self._throw_on_failure = value

    @property
    def expected_exit_code(self):
        return self._expected_exit_code

    @expected_exit_code.setter
    def expected_exit_code(self, value):
        self._expected_exit_code = value

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    def _execute(self, command, cwd, return_output, throw_on_failure, expected_exit_code):
        self.log.debug(command)
        if (return_output):
            process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, err = process.communicate()
            exit_code = process.returncode
            if not output.rstrip() and len(output.rstrip()) > 0:
                self.log.debug(output)
            if exit_code != expected_exit_code and throw_on_failure:
                raise ProcessError(command, exit_code, output)
            else:
                self.log.debug('Exit Code: {0}'.format(exit_code))
                self.log.debug(output)
                if throw_on_failure:
                    return output
                else:
                    return (output, exit_code)
        else:
            process = subprocess.Popen(command, cwd=cwd, shell=True)
            process.communicate()
            exit_code = process.returncode
            if exit_code != expected_exit_code and throw_on_failure:
                raise ProcessError(command, exit_code)
            else:
                return exit_code

    def _run(self, parsed_args, unknown_args, original_arguments):
        return self._execute(self.command, self.cwd, self.return_output, self.throw_on_failure, self.expected_exit_code)


class DockerCommand(Command):
    pass
