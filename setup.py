#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python setuptools install script.

Run with "python setup.py install" to install FlickrAPI
"""

from __future__ import print_function

__author__ = 'Sybren A. Stuvel'

# Check the Python version
import re
import io
import os
import sys

(major, minor) = sys.version_info[:2]

if (major, minor) < (2, 7) or (major == 3 and minor < 4):
    raise SystemExit("Sorry, Python 2.7, or 3.4 or newer required")

from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []
test_deps = [
    'mock;python_version<"3.3"',
    "pytest>=2.9.1",
    "pytest-cov>=2.2.1",
    "responses>=0.5.1"
]

data = {
    'name': 'flickrapi',
    'version': find_version("flickrapi", "__init__.py"),
    'author': __author__,
    'author_email': 'sybren@stuvel.eu',
    'maintainer': __author__,
    'maintainer_email': 'sybren@stuvel.eu',
    'url': 'https://stuvel.eu/flickrapi',
    'description': 'The Python interface to the Flickr API',
    'long_description': 'The easiest to use, most complete, and '
                        'most actively developed Python interface to the Flickr API.'
                        'It includes support for authorized and non-authorized '
                        'access, uploading and replacing photos, and all Flickr API '
                        'functions.',
    'packages': ['flickrapi'],
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
    'setup_requires': pytest_runner,
    'tests_require': test_deps,
    'install_requires': [
        'six>=1.5.2',
        'requests>=2.2.1',
        'requests_oauthlib>=0.4.0',
        'requests_toolbelt>=0.3.1',
    ],
    'extras_require': {
        'docs': [
            'sphinx >= 1.5.1'
        ],
        'qa': [
            'flake8'
        ],
        'test': test_deps
    },
    'zip_safe': True,
    'test_suite': 'tests',
}

setup(**data)
