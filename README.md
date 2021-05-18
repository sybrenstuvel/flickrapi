Python FlickrAPI
================

[![Build
Status](https://travis-ci.org/sybrenstuvel/flickrapi.svg?branch=master)](https://travis-ci.org/sybrenstuvel/flickrapi)
[![Coverage
Status](https://coveralls.io/repos/github/sybrenstuvel/flickrapi/badge.svg?branch=master)](https://coveralls.io/github/sybrenstuvel/flickrapi?branch=master)




Getting Started
---------------

Most of the info can be found in the `doc` directory, or on
https://stuvel.eu/flickrapi

To install the latest version from PyPi:

    pip install flickrapi

To install the Python Flickr API module from source into a virtualenv, run::

    pip install --user poetry
    poetry install

For development, install the dependencies using:

    poetry install --extras 'docs qa'

then run `poetry run py.test` in the top-level directory.

Supported Python versions
-------------------------

The minimum Python version that is supported is 3.5.

As of March 2019, [Python 3.4 stopped receiving security
updates](https://www.python.org/downloads/release/python-3410/),
at which time this library also stopped supporting it.

Improvements to maintain functionality in 3.9+ are coming.

Generating the documentation
----------------------------

The documentation is written using [Sphinx](http://www.sphinx-doc.org).
Execute `make html` in the `doc` directory to generate the HTML pages.
They can then be found in the `doc/_build/html` directory.

Tests
-----

Run the tests on all supported Python versions with Tox
(`pip install tox`):

    tox

To run the tests for a specific Python version, e.g. 3.6:

    tox -e py36

Maintenance
----------------------------

**For maintenance information or other concerns (i.e. to get your PR reviewed) contact me at <goode.cameron@yahoo.com>**
