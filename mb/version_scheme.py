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

    def generate(self):
        self.log.info('Generating Version...')
        generated_version = self._generate()
        self.log.info('Version: {0}'.format(generated_version))
        return generated_version

    @abc.abstractmethod
    def _generate(self):
        raise NotImplementedError("'generate' must be reimplemented by %s" % self)


class Increment(Enum):
    none = 0
    patch = 1


class DefaultVersionScheme(VersionScheme):
    def __init__(self, config):
        super(DefaultVersionScheme, self).__init__()
        self.repo = Repo(config.project_dir)
        self._version = None
        self._increment = Increment.none

    def _describe(self, value):
        try:
            return self.repo.git.describe(value, match=True)
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
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = Increment[value]

    def _return_version(self, version):
        hash = str(self.repo.head.commit)
        return {"hash": hash, "short_hash": hash[:7], "version": version}

    def _generate(self):
        if self.increment == Increment.none:
            return self._return_version(self.version)

        if not self.version:
            last_tag = self._describe('*[^a-z].*[^a-z].*[^a-z]')
        else:
            last_tag = self._describe('{0}.*[^a-z]'.format(self.version))

        if not last_tag:
            return self._return_version('{0}'.format(self.version))

        # this means that the current commit already has a tag, just return it
        if '-' not in last_tag:
            return self._return_version(last_tag)

        last_tag_split = last_tag.split('-')[0].split('.')
        prefix = '.'.join(last_tag_split[:-1])
        patch = int(last_tag_split[-1]) + 1
        calculated_version = '{0}.{1}'.format(prefix, patch)
        return self._return_version(calculated_version)
