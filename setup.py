#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

from distutils.core import setup, Distribution
import os

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
    'maintainer': 'Sybren Stüvel',
    'maintainer_email': 'sybren@stuvel.eu',
    'description': 'Python interface to the Flickr API', 
    'packages': ['flickrapi'],
    'data_files': [],
    'license': 'Python',
    'distclass': OurDistribution
}

alldocs = ['doc/documentation.html', 'doc/documentation.css', 'doc/html4css1.css']

if docutils or all(os.path.exists(doc) for doc in alldocs):
    # Only include documentation if it can be built, or if it has been
    # built already
    data['data_files'].append(('share/doc/flickrapi-%s' % __version__, alldocs))
    documentation_available = True
else:
    print "WARNING: Unable to import docutils, documentation will not be included"

setup(**data)
