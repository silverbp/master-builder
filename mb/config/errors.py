from __future__ import absolute_import
from __future__ import unicode_literals


class ConfigurationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class DependencyError(ConfigurationError):
    pass


class JarvisFileNotFound(ConfigurationError):
    def __init__(self, supported_filenames):
        super(JarvisFileNotFound, self).__init__("""
        Can't find a suitable configuration file in this directory or any
        parent. Are you in the right directory?

        Supported filenames: %s
        """ % ", ".join(supported_filenames))