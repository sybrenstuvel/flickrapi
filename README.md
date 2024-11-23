Python FlickrAPI
================

> [!CAUTION]
> This repository is no longer maintained. Bug reports will not be closed, pull requests will not be pulled. Please fork the project, or implement it from scratch.

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
