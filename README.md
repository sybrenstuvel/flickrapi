Python FlickrAPI
================

[![Build
Status](https://travis-ci.org/sybrenstuvel/flickrapi.svg?branch=master)](https://travis-ci.org/sybrenstuvel/flickrapi)
[![Coverage
Status](https://coveralls.io/repos/github/sybrenstuvel/flickrapi/badge.svg?branch=master)](https://coveralls.io/github/sybrenstuvel/flickrapi?branch=master)

Most of the info can be found in the `doc` directory, or on
https://stuvel.eu/flickrapi

To install the Python Flickr API module from source, run::

    python setup.py install

To install the latest version from PyPi:

    pip install flickrapi

For development, install the extra dependencies using:

    pip install tox .[docs] .[qa] .[test]

then run `py.test` in the top-level directory.

Supported Python versions
-------------------------

The minimum Python versions that are supported are 2.7 and 3.4.

[Python 2.7 will be discontinued in 2020](http://www.i-programmer.info/news/216-python/7179-python-27-to-be-maintained-until-2020.html),
which also marks the end of the support for Python 2.x for this
library. We might discontinue supporting Python 2.x earlier than that,
but only if there is a very compelling reason to do so.

As of September 2017, [Python 3.3 stopped receiving security
updates](https://www.python.org/dev/peps/pep-0398/#lifespan),
at which time this library also stopped supporting it.

Generating the documentation
----------------------------

The documentation is written using [Sphinx](http://www.sphinx-doc.org).
Execute `make html` in the `doc` directory to generate the HTML pages.
They can then be found in the `doc/_build/html` directory.

Tests
-----

Run the tests on all supported Python versions with tox
(`pip install tox`)::

  tox

To run the tests for a specific Python version, e.g. 2.7::

  tox -e py27
