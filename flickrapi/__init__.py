#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A FlickrAPI interface.

The main functionality can be found in the `flickrapi.FlickrAPI`
class.

See `the FlickrAPI homepage`_ for more info.

.. _`the FlickrAPI homepage`: http://stuvel.eu/projects/flickrapi
"""
from __future__ import unicode_literals

# Copyright (c) 2007-2018 by the respective coders, see
# http://stuvel.eu/flickrapi
#
# This code is subject to the Python licence, as can be read on
# http://www.python.org/download/releases/2.5.2/license/
#
# For those without an internet connection, here is a summary. When this
# summary clashes with the Python licence, the latter will be applied.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Import the core functionality into the flickrapi namespace
from flickrapi.core import FlickrAPI

from flickrapi.xmlnode import XMLNode
from flickrapi.exceptions import (IllegalArgumentException,
    FlickrError, CancelUpload, LockingError)
from flickrapi.cache import SimpleCache
from flickrapi.tokencache import (OAuthTokenCache, TokenCache, SimpleTokenCache,  # noqa: F401
    LockingTokenCache)

__version__ = '2.4.0'
__all__ = ('FlickrAPI', 'IllegalArgumentException', 'FlickrError',
           'CancelUpload', 'LockingError', 'XMLNode', 'set_log_level', '__version__',
           'SimpleCache', 'TokenCache', 'SimpleTokenCache', 'LockingTokenCache')
__author__ = 'Sybren Stüvel'


def set_log_level(level):
    """Sets the log level of the logger used by the FlickrAPI module.

    >>> import flickrapi
    >>> import logging
    >>> flickrapi.set_log_level(logging.INFO)
    """

    import flickrapi.core
    import flickrapi.tokencache

    flickrapi.core.LOG.setLevel(level)
    flickrapi.tokencache.LOG.setLevel(level)


if __name__ == "__main__":
    print("Running doctests")
    import doctest

    doctest.testmod()
    print("Tests OK")
