from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import json
import os
import os.path

from mb.lib import logger


class BuildContext(object):
    def __init__(self):
        self.log = logger.get_logger('[BuildContext]')
        self.log.debug('Initializing {0}'.format(self.__class__.__name__))
        return

    @abc.abstractproperty
    def variables(self):
        raise NotImplementedError("'variables' must be reimplemented by %s" % self)

    @abc.abstractmethod
    @variables.setter
    def variables(self, value):
        raise NotImplementedError("'variables setter' must be reimplemented by %s" % self)


class DefaultBuildContext(BuildContext):
    def __init__(self, config):
        BuildContext.__init__(self)
        self.config = config
        self.build_context_file = os.path.join(config.artifact_dir, 'build_context.json')

    @property
    def variables(self):
        if os.path.isfile(self.build_context_file):
            with open(self.build_context_file, 'r') as buildvarfile:
                return json.load(buildvarfile)

        return {}

    @variables.setter
    def variables(self, value):
        data = {}
        if os.path.isfile(self.build_context_file):
            with open(self.build_context_file, 'r') as buildvarfile:
                data = json.load(buildvarfile)

        for key, value in value.iteritems():
            data[key] = value

        with open(self.build_context_file, 'w+') as jsonFile:
            jsonFile.write(json.dumps(data))
