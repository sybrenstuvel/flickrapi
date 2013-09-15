======================================================================
Python FlickrAPI
======================================================================

Most of the info can be found in the 'doc' directory or on
http://stuvel.eu/flickrapi

To install the Python Flickr API module from source, run::

    python setup.py install

To install the latest version from PyPi:

    pip install flickrapi

For development, install extra dependencies using::
    
    pip install -r requirements.txt 

then run ``nosetest`` in the top-level directory.

Generating the documentation
--------------------------------------------------

The documentation is written in Sphynx. Execute 'make html' in the doc
directory to generate the HTML pages. They can then be found in
doc/_build/html.
