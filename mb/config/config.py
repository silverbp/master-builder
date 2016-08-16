from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os
import re
from collections import namedtuple

import six
import yaml
from jsonpath_rw import parse

from ..lib import logger
from ..lib.memoize import memoize
from .errors import ConfigurationError
from .errors import MasterBuilderFileNotFoundError
from .interpolation import interpolate_value

SUPPORTED_FILENAMES = [
    '.mb.yml',
    '.mb.yaml',
    '.mb.json'
]

_log = logger.get_logger('[Config]')


class ConfigFile(namedtuple('_ConfigFile', 'filename config')):
    """
    :param filename: filename of the config file
    :type  filename: string
    :param config: contents of the config file
    :type  config: :class:`dict`
    """

    @classmethod
    def from_yaml_file(cls, filename, mappings=None):
        return cls(filename, load_yaml(filename, mappings))

    @classmethod
    def from_json_file(cls, filename, mappings=None):
        return cls(filename, load_json(filename, mappings))

    @property
    def project_dir(self):
        file = os.path.abspath(self.filename)
        return os.path.dirname(file)

    @memoize
    def get_value(self, value):
        jsonpath_expr = parse(value)
        for match in jsonpath_expr.find(self.config):
            return self._expand_value(match.value)

        if value in _build_defaults:
            return _build_defaults[value]

        return None

    @memoize
    def get_values(self, value):
        return_list = []

        jsonpath_expr = parse(value)
        for match in jsonpath_expr.find(self.config):
            return_list.append(self._expand_value(match.value, self))

        if len(return_list) > 0:
            return return_list

        if value in _build_defaults:
            return _build_defaults[value]

        return None

    def _expand_value(self, value):
        if not isinstance(value, six.string_types):
            return value

        value = re.sub(r"\@\{\{.+?\}\}", lambda m: self.get_value(m.group()[3:-2]), value)

        if (value.startswith('file://')):
            return self._expand_file(value[7:])

        return value

    def _expand_file(self, file):
        split_file = file.split('@')
        if len(split_file) != 2:
            raise ConfigurationError("""
                Invalid file reference: {file},
                You must specify a JsonPath by appending @ with the JsonPath on the file
                """.format({file: file}))

        file_name = split_file[0]
        json_path = split_file[1]

        if file_name.endswith('yaml') or file_name.endswith('yml'):
            return ConfigFile.from_yaml_file(file_name).get_value(json_path)

        if file_name.endswith('json'):
            return ConfigFile.from_json_file(file_name).get_value(json_path)

        raise ConfigurationError(u"Invalid file reference: {file}, You can only use a json or yaml file."
                                 .format({file: file}))


def load_yaml(filename, mappings=None):
    try:
        with open(filename, 'r') as fh:
            return_yaml = yaml.safe_load(fh)
            if mappings:
                return interpolate_value(return_yaml, mappings)
            return return_yaml
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise ConfigurationError(u"{}: {}".format(error_name, e))


def load_json(filename, mappings=None):
    try:
        with open(filename, 'r') as fh:
            return_json = json.load(fh)
            if mappings:
                return interpolate_value(return_json, mappings)
            return return_json
    except Exception as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise ConfigurationError(u"{}: {}".format(error_name, e))


def get_default_config_file(base_dir="./", mappings=os.environ):
    (candidates, path) = find_candidates_in_parent_dirs(SUPPORTED_FILENAMES, base_dir)

    if not candidates:
        raise MasterBuilderFileNotFoundError(SUPPORTED_FILENAMES)

    winner = candidates[0]

    if len(candidates) > 1:
        _log.warn("Found multiple config files with supported names: %s", ", ".join(candidates))
        _log.warn("Using %s\n", winner)

    if (winner.endswith('json')):
        return ConfigFile.from_json_file(os.path.join(path, winner), mappings)

    return ConfigFile.from_yaml_file(os.path.join(path, winner), mappings)


def find_candidates_in_parent_dirs(filenames, path):
    """
    Given a directory path to start, looks for filenames in the
    directory, and then each parent directory successively,
    until found.

    Returns tuple (candidates, path).
    """
    candidates = [filename for filename in filenames
                  if os.path.exists(os.path.join(path, filename))]

    if not candidates:
        parent_dir = os.path.join(path, '..')
        if os.path.abspath(parent_dir) != os.path.abspath(path):
            return find_candidates_in_parent_dirs(filenames, parent_dir)

    return (candidates, path)


_build_defaults = {
    'config.version_scheme': 'DefaultVersionScheme',
    'config.template_engine': 'DefaultTemplateEngine',
    'version': '1',
    'log_level': 'INFO'
}
