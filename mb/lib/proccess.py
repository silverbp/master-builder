from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess

import logger

_log = logger.get_logger('[Process]')


class Error(Exception):
    def __init__(self, command, exitCode, output=''):
        self.message = output
        self.command = command
        self.exitCode = exitCode

    def __str__(self):
        return repr(self.exitCode)


def execute(command, cwd="./", return_output=True, throw_on_failure=True, expected_exit_code=0):
    _log.debug(command)
    if (return_output):
        process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, err = process.communicate()
        exit_code = process.returncode
        if not output.rstrip() and len(output.rstrip()) > 0:
            _log.debug(output)
        if exit_code != expected_exit_code and throw_on_failure:
            raise Error(command, exit_code, output)
        else:
            _log.debug('Exit Code: {0}'.format(exit_code))
            _log.debug(output)
            if throw_on_failure:
                return output
            else:
                return (output, exit_code)
    else:
        process = subprocess.Popen(command, cwd=cwd, shell=True)
        process.communicate()
        exit_code = process.returncode
        if exit_code != expected_exit_code and throw_on_failure:
            raise Error(command, exit_code)
        else:
            return exit_code
