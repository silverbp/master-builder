from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import sys

from mb.lib import logger

if '--verbose' in sys.argv[1:]:
    logger.set_log_level('DEBUG')

from mb.lib import ioc # NOQA


def run_command(command, arguments=[]):
    loaded_command = ioc.load_command(command)
    loaded_command.wrapped_run(arguments)


def main():
    parser = argparse.ArgumentParser(prog='Master Builder',
                                     description='Build Ochestration Tool')
    arguments = sys.argv[1:]
    commands = ioc.get_commands()

    # handle potential default command allowing you to do build without a subcommand.
    subcommand = ''

    if 'default' in commands:
        if len(arguments) < 1:
            subcommand = 'default'
        elif (arguments[0].startswith('-') or arguments[0].startswith('--')) and (arguments[0] != '-h' and arguments[0] != '--help'):
            subcommand = 'default'
        else:
            subcommand = arguments[0]
            arguments = arguments[1:]
    elif len(arguments) > 0:
        subcommand = arguments[0]
        arguments = arguments[1:]

    # get subcommands dynamically and fill out choices
    parser.add_argument('subcommand', choices=commands, help='The build subcommand you want to run')
    parser.add_argument('--verbose', action='store_true', help='Enables Verbose output for build commands')

    args = parser.parse_args([subcommand])
    run_command(args.subcommand, arguments)
