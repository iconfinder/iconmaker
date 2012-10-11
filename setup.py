import os
from distutils.core import setup

# Dynamically calculate the version based on tagging.VERSION.
#version_tuple = __import__('iconmaker').VERSION
#if version_tuple[2] is not None:
#    version = "%d.%d_%s" % version_tuple
#else:
#    version = "%d.%d" % version_tuple[:2]

setup(
    name = 'iconmaker',
    version = '1.0',
    url = 'http://www.iconfinder.com',
    license = 'LICENSE.txt'
    description = 'Icon conversion utility'
    long_description = open('README.txt').read(),
    package_dir = {'iconmaker': 'iconmaker'},
    packages = ['iconmaker', 
                'iconmaker.tests'],
    package_data = {'iconmaker':[
                        glob('tests/icons/*'),
                    ]},
    install_requires = ['PIL >= 1.1.7',
                        'requests >= 0.14.1'
    ],
)