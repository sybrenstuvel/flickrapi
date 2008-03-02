#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

from distutils.core import setup, Distribution
import os
import sys

try:
    import docutils.core
except ImportError:
    docutils = None

from flickrapi import __version__

# This will be set to True when either the documentation is already
# there, or if we can build it.
documentation_available = False

class OurDistribution(Distribution):
    '''Distribution that also generates the documentation HTML'''

    def run_command(self, command):
        '''Builds the documentation if needed, then passes control to
        the superclass' run_command(...) method.
        '''

        if command == 'install_data' and docutils:
            publisher = docutils.core.Publisher()
            docutils.core.publish_file(writer_name='html',
                    source=open('doc/documentation.rst'),
                    source_path='doc',
                    destination=open('doc/documentation.html', 'w'),
                    destination_path='doc',
                    settings_overrides={'stylesheet_path': 'doc/documentation.css'}
            )
        Distribution.run_command(self, command)

data = {
    'name': 'flickrapi', 
    'version': __version__, 
    'url': 'http://flickrapi.sourceforge.net/', 
    'author': 'Beej Jorgensen', 
    'author_email': 'beej@beej.us', 
    'maintainer': 'Sybren Stuvel',
    'maintainer_email': 'sybren@stuvel.eu',
    'description': 'The official Python interface to the Flickr API', 
    'long_description': 'The easiest to use, most complete, and '
        'most actively developed Python interface to the Flickr API.'
        'It includes support for authorized and non-authorized '
        'access, uploading and replacing photos, and all Flickr API '
        'functions.', 
    'packages': ['flickrapi'],
    'data_files': [],
    'license': 'Python',
    'classifiers': [
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python License (CNRI Python License)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'distclass': OurDistribution
}

# Check the Python version
(major, minor) = sys.version_info[:2]

if major < 2 or (major == 2 and minor < 4):
    raise SystemExit("Sorry, Python 2.4 or newer required")

if major == 2 and minor < 5:
    # We still want to use this function, but Python 2.4 doesn't have
    # it built-in.
    def all(iterator):
        for item in iterator:
            if not item: return False
        return True

alldocs = ['doc/documentation.html', 'doc/documentation.css', 'doc/html4css1.css']

if docutils or all(os.path.exists(doc) for doc in alldocs):
    # Only include documentation if it can be built, or if it has been
    # built already
    data['data_files'].append(('share/doc/flickrapi-%s' % __version__, alldocs))
    documentation_available = True
else:
    print "======================================================================="
    print "WARNING: Unable to import docutils, documentation will not be included"
    print "Documentation for the latest version can be found at"
    print "http://flickrapi.sourceforge.net/documentation"
    print "======================================================================="
    print

setup(**data)
