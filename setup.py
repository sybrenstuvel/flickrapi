#!/usr/bin/env python

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

import sys

# Check the Python version
(major, minor) = sys.version_info[:2]

if (major, minor) < (2, 4):
    raise SystemExit("Sorry, Python 2.4 or newer 2.x version required")

if major >= 3:
    raise SystemExit('Sorry, Python 3.x is not supported. Support was '
    'introduced in version 2.0; you may want to upgrade to that one.')

import _setup
