from __future__ import absolute_import
from __future__ import unicode_literals

from string import Template

import six

from ..lib.logger import get_logger
from .errors import ConfigurationError
log = get_logger(__name__)


def interpolate_value(value, mapping):
    try:
        return recursive_interpolate(value, mapping)
    except InvalidInterpolation as e:
        raise ConfigurationError(
            'Invalid interpolation format'
            'in "{value}": "{string}"'.format(
                value=value,
                string=e.string))


def recursive_interpolate(obj, mapping):
    if isinstance(obj, six.string_types):
        return interpolate(obj, mapping)
    elif isinstance(obj, dict):
        return dict(
            (key, recursive_interpolate(val, mapping))
            for (key, val) in obj.items()
        )
    elif isinstance(obj, list):
        return [recursive_interpolate(val, mapping) for val in obj]
    else:
        return obj


def interpolate(string, mapping):
    try:
        return Template(string).safe_substitute(mapping)
    except ValueError:
        raise InvalidInterpolation(string)


class InvalidInterpolation(Exception):
    def __init__(self, string):
        self.string = string
