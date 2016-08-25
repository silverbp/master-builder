from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import sys

from mb.lib import logger

if '--verbose' in sys.argv[1:]:
    logger.set_log_level('DEBUG')

from mb.lib import ioc # NOQA
already_ran = []


def run_command(command, arguments=[]):
    if command in already_ran:
        return

    already_ran.append(command)
    loaded_command = ioc.load_command(command)
    for dep_command in loaded_command.dependencies:
        run_command(dep_command, arguments)

    loaded_command.run(arguments)


def main():
    parser = argparse.ArgumentParser(prog='mb',
                                     description='Master Builder: Build Ochestration')
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
