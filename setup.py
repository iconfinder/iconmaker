#!/usr/bin/env python
"""
iconmaker
=========

iconmaker is a simple Python library providing an interface for easily 
converting PNG or GIF source files to Microsoft Windows ICO or Apple Mac ICNS 
icon container formats.
"""

from setuptools import setup, find_packages

tests_require = [
    'nose', 
    'mysql-connector-repackaged'
]

install_requires = [
#    'PIL>=1.1.7', 
    'requests>=0.14.1', 
]

setup(
    name = 'iconmaker', 
    version = '1.0.0', 
    url = 'http://www.iconfinder.com', 
    description = 'Icon conversion utility', 
    long_description = __doc__, 
    packages = find_packages(exclude = ['tests', 
                                        '.*', 
                                        'venv']), 
    install_requires = install_requires, 
    tests_require = tests_require, 
    extras_require = {
        'test': tests_require
    },
)
