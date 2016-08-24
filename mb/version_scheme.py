from __future__ import absolute_import
from __future__ import unicode_literals

import abc

from enum import Enum
from git import exc as git_exc
from git import Repo

from .lib import logger


class VersionScheme(object):
    def __init__(self):
        self.log = logger.get_logger('[VersionScheme]')
        self.log.debug('Initializing {0}'.format(self.__class__.__name__))
        return

    @abc.abstractmethod
    def generate(self):
        raise NotImplementedError("'generate' must be reimplemented by %s" % self)


class Increment(Enum):
    none = 0
    patch = 1


class DefaultVersionScheme(VersionScheme):
    def __init__(self, config):
        VersionScheme.__init__(self)
        self.repo = Repo(config.project_dir)
        self._version = "1.0"
        self._increment = Increment.none

    def _describe(self, value):
        try:
            return self.repo.git.describe(value)
        except git_exc.GitCommandError as err:
            if 'No names found' in str(err):
                return None
            raise err

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def increment(self):
        return self._increment.value

    @increment.setter
    def increment(self, value):
        if value in Increment:
            self._increment = Increment[value]

    def generate(self):
        if not self.version:
            last_tag = self._describe('\*\[^a-z\].\*\[^a-z\].\*\[^a-z\]')
        else:
            last_tag = self._describe('{0}.\*\[^a-z\]'.format(self.version))

        if not last_tag:
            return '{0}.0'.format(self.version)

        # this means that the current commit already has a tag, just return it
        if '-' not in last_tag or self.increment == Increment.none:
            return last_tag

        last_tag_split = last_tag.split('-')[0].split('.')
        major = int(last_tag_split[0])
        minor = int(last_tag_split[1])
        patch = int(last_tag_split[2]) + 1
        calculated_version = '{0}.{1}.{2}'.format(major, minor, patch)
        return calculated_version
