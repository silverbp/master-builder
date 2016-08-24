from __future__ import absolute_import
from __future__ import unicode_literals

import os

from mb.config.config import ConfigFile
from mb.config.config import get_default_config_file
# import pytest
# from mb.config.errors import MasterBuilderFileNotFoundError

_project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
_testConfig = {
    'name': 'sample_config'
}


def test_config_file_load():
    config = get_default_config_file("tests/fixtures", os.environ)
    assert config.get_command("default").name == "DemoCommand"
    assert config.variables["version"] == "2.0.0"


# def test_config_file_load_doesnt_exist():
#     # This will pass until we start using Master Builder to build Master Builder :)
#     with pytest.raises(MasterBuilderFileNotFoundError):
#         get_default_config_file("./", os.environ)


def test_project_dir():
    # it doesn't actually read the file, it only uses it as a reference to figure
    # out where the project root is, so I'll use .gitignore for the test
    assert ConfigFile(".gitignore", _testConfig).project_dir == _project_dir


def test_artifact_dir():
    config = ConfigFile(".gitignore", _testConfig)
    assert config.artifact_dir == os.path.join(_project_dir, '.build')
    assert os.path.exists(config.artifact_dir)
    os.rmdir(config.artifact_dir)


def test_custom_artifact_dir():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'config': {
            'artifact_dir': '.artifact'
        }
    })
    assert config.artifact_dir == os.path.join(_project_dir, '.artifact')
    assert os.path.exists(config.artifact_dir)
    os.rmdir(config.artifact_dir)


def test_default_version_scheme():
    config = ConfigFile(".gitignore", _testConfig)
    assert config.version_scheme.name == "DefaultVersionScheme"
    assert len(config.version_scheme.config) == 0


def test_configure_version_scheme():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'variables': {
            'version': '1.0.0'
        },
        'config': {
            'version_scheme': {
                'config': {
                    '@{{name}}': '@{{variables.version}}'
                }
            }
        }
    })

    assert config.version_scheme.config['sample_config'] == '1.0.0'


def test_default_template_engine():
    config = ConfigFile(".gitignore", _testConfig)
    assert config.template_engine.name == "DefaultTemplateEngine"
    assert len(config.template_engine.config) == 0


def test_configure_template_engine():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'variables': {
            'foo': 'bar'
        },
        'config': {
            'template_engine': {
                'config': {
                    '@{{name}}': '@{{variables.foo}}'
                }
            }
        }
    })

    assert config.template_engine.config['sample_config'] == 'bar'


def test_default_build_context():
    config = ConfigFile(".gitignore", _testConfig)
    assert config.build_context.name == "DefaultBuildContext"
    assert len(config.build_context.config) == 0


def test_configure_build_context():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'variables': {
            'foo': 'bar'
        },
        'config': {
            'build_context': {
                'config': {
                    '@{{name}}': '@{{variables.foo}}'
                }
            }
        }
    })

    assert config.build_context.config['sample_config'] == 'bar'


def test_get_variables():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'variables': {
            'foo': 'bar',
            '@{{variables.foo}}': 'file://tests/fixtures/sample.source.json@version'
        }
    })

    assert config.variables['foo'] == 'bar'
    assert config.variables['bar'] == '2.0.0'


def test_get_empty_variables():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config'
    })

    assert config.variables == {}


def test_commands():
    config = ConfigFile(".gitignore", {
        'name': 'sample_config',
        'variables': {
            'some_var': 'test'
        },
        'config': {
            'commands': {
                'default': {
                    'name': 'DemoCommand',
                    'config': {
                        '@{{name}}': '@{{variables.some_var}}'
                    }
                }
            }
        }
    })

    assert config.commands['default'].name == 'DemoCommand'
    assert config.commands['default'].config['sample_config'] == 'test'
