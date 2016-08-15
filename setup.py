#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'cached-property >= 1.2.0, < 2',
    'docopt >= 0.6.1, < 0.7',
    'PyYAML >= 3.10, < 4',
    'requests >= 2.6.1, < 2.8',
    'texttable >= 0.8.1, < 0.9',
    'websocket-client >= 0.32.0, < 1.0',
    'docker-py >= 1.9.0, < 2.0',
    'dockerpty >= 0.4.1, < 0.5',
    'six >= 1.3.0, < 2',
    'jsonschema >= 2.5.1, < 3',
]


tests_require = [
    'pytest',
]

setup(
    name='Master-Builder Build System',
    version='1.0.0',
    description='A Universal/Plugable Build System',
    url='https://github.com/silverbp/master-builder',
    author='Silver Blueprints LLC',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    test_suite='nose.collector',
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points="""
    [console_scripts]
    mb=mb.cli.main:main
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
