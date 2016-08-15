from __future__ import absolute_import
from __future__ import unicode_literals

import json
import re
from collections import namedtuple

import six
import yaml
from jsonpath_rw import parse

from ..lib.memoize import memoize
from .errors import ConfigurationError
from .interpolation import interpolate_value


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

    @memoize
    def get_value(self, value):
        jsonpath_expr = parse(value)
        for match in jsonpath_expr.find(self.config):
            return expand_value(match.value, self)

        if value in _build_defaults:
            return _build_defaults[value]

        return None

    @memoize
    def get_values(self, value):
        return_list = []
        jsonpath_expr = parse(value)
        for match in jsonpath_expr.find(self.config):
            return_list.append(expand_value(match.value, self))

        if len(return_list) > 0:
            return return_list

        if value in _build_defaults:
            return _build_defaults[value]

        return None


def expand_file(file, config):
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


def expand_value(value, configFile):
    if not isinstance(value, six.string_types):
        return value

    value = re.sub(r"\@\{\{.+?\}\}", lambda m: configFile.get_value(m.group()[3:-2]), value)

    if (value.startswith('file://')):
        return expand_file(value[7:], configFile.config)

    return value


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


_build_defaults = {
    'plugins.build_context': 'DefaultBuildContext',
    'plugins.artifact_store': 'DirectoryArtifactStore',
    'plugins.version_scheme': 'DockerBaseImageScheme',
    'plugins.template_engine': 'DefaultTemplateEngine',
    'log_level': 'INFO'
}
