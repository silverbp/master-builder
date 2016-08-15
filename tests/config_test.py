from __future__ import absolute_import
from __future__ import unicode_literals

import os

from mb.config.config import ConfigFile


class TestConfig:
    configFile = ConfigFile.from_yaml_file("tests/fixtures/sample.mb.yml", os.environ)

    def test_config_load(self):
        assert self.configFile.get_value('name') == 'sample'
        assert self.configFile.get_value('plugins.version_scheme') == 'TestVersionScheme'

    def test_config_default_values(self):
        assert self.configFile.get_value('plugins.build_context') == 'DefaultBuildContext'

    def test_config_external_file(self):
        assert self.configFile.get_value('build.version') == '1.0.0'

    def test_config_interoplation(self):
        assert self.configFile.get_value('build.image_name') == 'silverbp.io/sample:1.0.0'

    def test_config_env(self):
        print(self.configFile.get_value('build.image_name'))
