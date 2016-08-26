from __future__ import absolute_import
from __future__ import unicode_literals

import glob
import imp
import inspect
import os
import sys

from mb.config.config import get_default_config_file
from mb.lib import logger

_log = logger.get_logger('[Ioc]')

# plugin types
from mb import build_context # BuildContext # NOQA
from mb import command # Command # NOQA
from mb import template_engine # TemplateEngine # NOQA
from mb import version_scheme #VersionScheme # NOQA
from mb.config.config import PluginConfig # NOQA


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def _is_plugin_type(object_attr, plugin_type):
    try:
        if object_attr == plugin_type:
            return False

        return issubclass(object_attr, plugin_type)
    except:
        return False


_plugin_modules = [build_context, command, template_engine, version_scheme]
_plugin_types = [build_context.BuildContext, command.Command, template_engine.TemplateEngine, version_scheme.VersionScheme]
_loaded_plugin_definitions = {}
_plugin_instances = {}
_config = get_default_config_file()

if os.path.isdir(_config.plugin_dir):
    os.chdir(_config.plugin_dir)
    for file in glob.glob("*.py"):
        plugin_module_name_template = "silverbp_mb_plugin_" + os.path.splitext(file)[0] + "_%d"
        for plugin_name_suffix in range(len(sys.modules)):
            plugin_module_name = plugin_module_name_template % plugin_name_suffix
            if plugin_module_name not in sys.modules:
                break
        with open(file, "r") as plugin_file:
            _plugin_modules.append(imp.load_module(plugin_module_name, plugin_file, file, ("py", "r", imp.PY_SOURCE)))

for module in _plugin_modules:
    for module_attr in (getattr(module, name) for name in dir(module)):
        for plugin_type in _plugin_types:
            if not _is_plugin_type(module_attr, plugin_type):
                continue

            _loaded_plugin_definitions[module_attr.__name__] = module_attr

_defined_commands = _config.commands
_defined_commands['_prerun'] = PluginConfig('MBPreRunCommand', {}, _config)

command_plugins = [k for (k, v) in _loaded_plugin_definitions.items() if _is_plugin_type(v, command.Command)]

for (k, v) in _config.commands.items():
    if v.name not in command_plugins:
        _log.warn('The following Command: {0} was not found and will not be available'.format(k))
        del _defined_commands[k]

_log.debug('The following commands will be available: {0}'.format([k for (k, v) in _defined_commands.items() if not k.startswith('_')]))


def _load_plugin(plugin):
    if plugin.name in _plugin_instances.keys():
        return _plugin_instances[plugin.name]

    plugin_definition = _loaded_plugin_definitions[plugin.name]
    arguments = []

    # if the plugin doesn't have a constructor, there's nothing to inject
    if '__init__' in getattr(plugin_definition, '__dict__', None).keys():
        for arg in inspect.getargspec(plugin_definition.__init__)[0][1:]:
            arguments.append(load_dependency(arg))

    instance = plugin_definition(*arguments)
    available_properties = [x for x, y in inspect.getmembers(instance.__class__, lambda x: isinstance(x, property))]

    for (key, value) in plugin.config.items():
        if key in available_properties:
            try:
                setattr(instance, key, value)
            except Exception as err:
                _log.warn('There was a problem setting the plugin config: \'{0}\' on \'{1}\' with \'{2}\'.'.format(plugin.name, key, value))
                _log.debug('Exception occured while trying to set a plugin config value: {0}'.format(err))
        else:
            _log.warn('The following plugin config: {0}, is not an option to set on {1}'.format(key, plugin.name))

    _plugin_instances[plugin.name] = instance
    return instance


def load_dependency(name):
    if name == 'config':
        return _config

    return _load_plugin(getattr(_config, name))


def get_commands():
    return [k for (k, v) in _defined_commands.items() if not k.startswith('_')]


def load_command(name):
    if name in _defined_commands.keys():
        plugin = _defined_commands[name]
    else:
        raise StandardError('The following command: {0} is not available'.format(name))

    return _load_plugin(plugin)
