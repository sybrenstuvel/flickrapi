#!/usr/bin/env python

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

import ez_setup
ez_setup.use_setuptools()

import sys

# Check the Python version
(major, minor) = sys.version_info[:2]

if major < 2 or (major == 2 and minor < 4):
    raise SystemExit("Sorry, Python 2.4 or newer required")

import _setup
