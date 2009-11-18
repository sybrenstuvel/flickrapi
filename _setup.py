# -*- encoding: utf-8 -*-

'''The setup code is split into two sections, one in setup.py which
contains very simple Python code and checks the Python version, and
this file, which contains code only parsable by 2.4+.
'''

__author__ = 'Sybren A. Stuvel'

from setuptools import setup, Distribution
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
    '''Distribution that also generates the flickrapi.html'''

    def run_command(self, command):
        '''Builds the documentation if needed, then passes control to
        the superclass' run_command(...) method.
        '''

        if command == 'install_data' and docutils:
            print 'creating doc/index.html'
            docutils.core.publish_file(writer_name='html',
                    source=open('doc/index.rst'),
                    source_path='doc',
                    destination=open('doc/index.html', 'w'),
                    destination_path='doc',
                    settings_overrides={'stylesheet_path':
                        'doc/documentation.css'}
            )
        Distribution.run_command(self, command)

data = {
    'name': 'flickrapi', 
    'version': __version__, 
    'author': 'Beej Jorgensen and Sybren A. Stuvel',
    'author_email': 'beej@beej.us', 
    'maintainer': 'Sybren A. Stuvel',
    'maintainer_email': 'sybren@stuvel.eu',
    'url': 'http://stuvel.eu/projects/flickrapi',
    'description': 'The official Python interface to the Flickr API', 
    'long_description': 'The easiest to use, most complete, and '
        'most actively developed Python interface to the Flickr API.'
        'It includes support for authorized and non-authorized '
        'access, uploading and replacing photos, and all Flickr API '
        'functions.', 
    'packages': ['flickrapi'],
    'data_files': ['LICENSE', 'README', 'UPGRADING'],
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
    'extras_require': {
        'ElementTree':  ["elementtree>=1.2.6"],
    },
    'distclass': OurDistribution,
    'zip_safe': True,
    'test_suite': 'tests',
}

(major, minor) = sys.version_info[:2]
if major == 2 and minor < 5:
    # We still want to use this function, but Python 2.4 doesn't have
    # it built-in.
    def all(iterator):
        for item in iterator:
            if not item: return False
        return True

alldocs = ['doc/index.html', 'doc/documentation.css', 'doc/html4css1.css']

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
