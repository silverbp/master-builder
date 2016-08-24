from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os
import re
from collections import namedtuple

import six
import yaml
from jsonpath_rw import parse

from mb.config.errors import ConfigurationError
from mb.config.errors import MasterBuilderFileNotFoundError
from mb.config.interpolation import interpolate_value
from mb.lib import logger
from mb.lib.memoize import memoize

SUPPORTED_FILENAMES = [
    '.mb.yml',
    '.mb.yaml',
    '.mb.json'
]

_log = logger.get_logger('[Config]')


class PluginConfig(namedtuple('_PluginConfig', 'name plugin_config master_config')):
    """
    Represents a Plugin type in the config file
    Commands, and any of the plugin types are represented by this class in the Configuration
    """

    @property
    def config(self):
        """
        Get the config settings for a Plugin type

        Returns:
            a dictionary of plugin config keys and values
        """
        return {_expand_value(self.master_config, key): _expand_value(self.master_config, value)
                for key, value in self.plugin_config.items()}


class ConfigFile(namedtuple('_ConfigFile', 'filename config')):
    """
    Represents the Master Builder Config File
    """

    @property
    def project_dir(self):
        """
        Get the project directory, this is based on where the Master Builder ConfigFile
        file is at.

        Returns:
            absolute path of the project directory
        """
        file = os.path.abspath(self.filename)
        return os.path.dirname(file)

    @property
    def artifact_dir(self):
        """
        Get the artifact directory.
        This is the directory used to store session or things that the build produces.
        You can configure this in the Master Builder config file with config.artifact_dir

        Returns:
            absolute path of the artifact directory
        """
        dir = os.path.join(self.project_dir, _get_value(self.config, 'config.artifact_dir', '.build'))
        if not os.path.exists(dir):
            _log.debug('artifact directory does not exist, creating it...')
            os.makedirs(dir)
        return dir

    @property
    def template_dir(self):
        return os.path.join(self.project_dir, _get_value(self.config, 'config.template_dir', 'build_templates'))

    @property
    def plugin_dir(self):
        return os.path.join(self.project_dir, _get_value(self.config, 'config.plugin_dir', '.build/plugins'))

    @property
    def version_scheme(self):
        default = "DefaultVersionScheme"
        plugin = _get_value(self.config, "config.version_scheme")
        if not plugin:
            return self._load_plugin_config(default)
        return self._load_plugin_config(plugin, default)

    @property
    def template_engine(self):
        default = "DefaultTemplateEngine"
        plugin = _get_value(self.config, "config.template_engine")
        if not plugin:
            return self._load_plugin_config(default)
        return self._load_plugin_config(plugin, default)

    @property
    def build_context(self):
        default = "DefaultBuildContext"
        plugin = _get_value(self.config, "config.build_context")
        if not plugin:
            return self._load_plugin_config(default)
        return self._load_plugin_config(plugin, default)

    @property
    def variables(self):
        variables = _get_values(self.config, "variables")
        if not variables:
            return {}

        variables = variables[0]
        return {_expand_value(self.config, key): _expand_value(self.config, value) for key, value in variables.items()}

    @property
    def commands(self):
        commands = _get_values(self.config, "config.commands")[0]
        return {key: self._load_plugin_config(value) for key, value in commands.items()}

    def get_command(self, command):
        return self._load_plugin_config(_get_value(self.config, "config.commands.{0}".format(command)))

    def _load_plugin_config(self, value, default_name=None):
        if isinstance(value, six.string_types):
            return PluginConfig(value, {}, self.config)

        if not isinstance(value, dict):
            raise ConfigurationError("A plugin config must be a dictionary or a string")

        if "name" in value:
            name = _expand_value(self.config, value["name"])
        else:
            name = default_name

        if "config" in value:
            config = value["config"]
            if not isinstance(config, dict):
                raise ConfigurationError("The config part of a plugin must be a dict: {0}".format(value))
        else:
            config = None

        if not name:
            raise ConfigurationError("A name is required for the following config plugin: {0}"
                                     .format(value))

        return PluginConfig(name, config, self.config)


def get_default_config_file(base_dir="./", mappings=os.environ):
    (candidates, path) = _find_candidates_in_parent_dirs(SUPPORTED_FILENAMES, base_dir)

    if not candidates:
        raise MasterBuilderFileNotFoundError(SUPPORTED_FILENAMES)

    winner = candidates[0]

    if len(candidates) > 1:
        _log.warn("Found multiple config files with supported names: %s", ", ".join(candidates))
        _log.warn("Using %s\n", winner)

    file = os.path.join(path, winner)
    if (winner.endswith('json')):
        return ConfigFile(file, _load_json(file, mappings))

    return ConfigFile(file, _load_yaml(file, mappings))


def _get_value(config, value, default_value=None):
    jsonpath_expr = parse(value)
    for match in jsonpath_expr.find(config):
        return _expand_value(config, match.value)

    return default_value


def _get_values(config, value):
    jsonpath_expr = parse(value)
    return [_expand_value(config, match.value) for match in jsonpath_expr.find(config)]


def _expand_value(config, value):
    if not isinstance(value, six.string_types):
        return value

    value = re.sub(r"\@\{\{.+?\}\}", lambda m: _get_value(config, m.group()[3:-2]), value)

    if (value.startswith('file://')):
        return _expand_file(value[7:])

    return value


def _expand_file(file):
    split_file = file.split('@')
    if len(split_file) != 2:
        raise ConfigurationError("""
            Invalid file reference: {file},
            You must specify a JsonPath by appending @ with the JsonPath on the file
            """.format({file: file}))

    file_name = split_file[0]
    json_path = split_file[1]

    loaded_file = None
    if file_name.endswith('yaml') or file_name.endswith('yml'):
        loaded_file = _load_yaml(file_name)

    if file_name.endswith('json'):
        loaded_file = _load_json(file_name)

    if loaded_file:
        return _get_value(loaded_file, json_path)

    raise ConfigurationError(u"Invalid file reference: {file}, You can only use a json or yaml file."
                             .format({file: file}))


@memoize("filename")
def _load_yaml(filename, mappings=None):
    try:
        with open(filename, 'r') as fh:
            return_yaml = yaml.safe_load(fh)
            if mappings:
                return interpolate_value(return_yaml, mappings)
            return return_yaml
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise ConfigurationError("{}: {}".format(error_name, e))


@memoize("filename")
def _load_json(filename, mappings=None):
    try:
        with open(filename, 'r') as fh:
            return_json = json.load(fh)
            if mappings:
                return interpolate_value(return_json, mappings)
            return return_json
    except Exception as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise ConfigurationError("{}: {}".format(error_name, e))


def _find_candidates_in_parent_dirs(filenames, path):
    candidates = [filename for filename in filenames
                  if os.path.exists(os.path.join(path, filename))]

    if not candidates:
        parent_dir = os.path.join(path, '..')
        if os.path.abspath(parent_dir) != os.path.abspath(path):
            return _find_candidates_in_parent_dirs(filenames, parent_dir)

    return (candidates, path)
