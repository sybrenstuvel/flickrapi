#!/usr/bin/env python

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

from __future__ import print_function

__author__ = 'Sybren A. Stuvel'
__version__ = '2.0-beta0'


# Check the Python version
import sys
(major, minor) = sys.version_info[:2]

if (major, minor) < (2, 6):
    raise SystemExit("Sorry, Python 2.6 or newer required")

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

data = {
    'name': 'flickrapi', 
    'version': __version__, 
    'author': 'Sybren A. Stuvel',
    'author_email': 'sybren@stuvel.eu', 
    'maintainer': 'Sybren A. Stuvel',
    'maintainer_email': 'sybren@stuvel.eu',
    'url': 'http://stuvel.eu/projects/flickrapi',
    'description': 'The official Python interface to the Flickr API', 
    'long_description': 'The easiest to use, most complete, and '
        'most actively developed Python interface to the Flickr API.'
        'It includes support for authorized and non-authorized '
        'access, uploading and replacing photos, and all Flickr API '
        'functions.', 
    'packages': ['flickrapi'],
    'data_files': ['LICENSE', 'README', 'UPGRADING'],
    'license': 'Python',
    'classifiers': [
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python License (CNRI Python License)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': [
        'requests==0.14.1', # 0.14.2 has a bug and won't install on Python 3.2
        'six>=1.2.0'
    ],
    'extras_require': {
        'ElementTree':  ["elementtree>=1.2.6"],
        'Sphinx': ["sphinx>=1.1.3"],
    },
    'zip_safe': True,
    'test_suite': 'tests',
}

setup(**data)
