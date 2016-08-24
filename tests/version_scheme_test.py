from __future__ import absolute_import
from __future__ import unicode_literals

import os

from mb.config.config import get_default_config_file
from mb.version_scheme import DefaultVersionScheme

config = get_default_config_file("tests/fixtures", os.environ)
defaultVersionScheme = DefaultVersionScheme(config)


def test_default_scheme():
    print(defaultVersionScheme.generate())
