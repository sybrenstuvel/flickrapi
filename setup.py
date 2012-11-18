#!/usr/bin/env python

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

import distribute_setup
distribute_setup.use_setuptools()

import sys

# Check the Python version
(major, minor) = sys.version_info[:2]

if (major, minor) < (2, 7):
    raise SystemExit("Sorry, Python 2.7 or newer required")

import _setup
