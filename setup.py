#!/usr/bin/env python

"""Python setuptools install script.

Run with "python setup.py install" to install FlickrAPI
"""

from __future__ import print_function

__author__ = 'Sybren A. Stuvel'
__version__ = '2.3.1'

# Check the Python version
import sys

(major, minor) = sys.version_info[:2]

if (major, minor) < (2, 7) or (major == 3 and minor < 4):
    raise SystemExit("Sorry, Python 2.7, or 3.4 or newer required")

from setuptools import setup

data = {
    'name': 'flickrapi',
    'version': __version__,
    'author': 'Sybren A. Stuvel',
    'author_email': 'sybren@stuvel.eu',
    'maintainer': 'Sybren A. Stuvel',
    'maintainer_email': 'sybren@stuvel.eu',
    'url': 'https://stuvel.eu/flickrapi',
    'description': 'The Python interface to the Flickr API',
    'long_description': 'The easiest to use, most complete, and '
                        'most actively developed Python interface to the Flickr API.'
                        'It includes support for authorized and non-authorized '
                        'access, uploading and replacing photos, and all Flickr API '
                        'functions.',
    'packages': ['flickrapi'],
    'package_data': {'flickrapi': ['../LICENSE.txt', '../README.md', '../UPGRADING.txt', '../CHANGELOG.md']},

    'license': 'Python',
    'classifiers': [
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python License (CNRI Python License)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': [
        'six>=1.5.2',
        'requests>=2.2.1',
        'requests_oauthlib>=0.4.0',
        'requests_toolbelt>=0.3.1',
    ],
    'extras_require': {
        'ElementTree': ["elementtree>=1.2.6"],
        'Sphinx': ["sphinx>=1.1.3"],
    },
    'zip_safe': True,
    'test_suite': 'tests',
}

setup(**data)
