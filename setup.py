#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'GitPython >= 2.0.8, < 2.1',
    'MarkupSafe >= 0.23, < 1.0',
    'PyYAML >= 3.11, < 4.0',
    'decorator >= 4.0.10, < 5.0',
    'docker-py >= 1.9.0, < 2.0',
    'jsonpath-rw >= 1.4.0, < 2.0',
    'pluggy >= 0.3.1, < 1.0',
    'ply >= 3.8, < 4.0',
    'py >= 1.4.31, < 2.0',
    'requests >= 2.11.0, < 3.0',
    'six >= 1.10.0, < 2.0',
    'websocket-client >= 0.37.0, < 1.0'
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
