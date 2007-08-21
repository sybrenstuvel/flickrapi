#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

from distutils.core import setup, Distribution
import os

from flickrapi import __version__

class OurDistribution(Distribution):
    '''Distribution that also generates the documentation HTML'''

    def run_command(self, command):
        '''Builds the documentation if needed, then passes control to
        the superclass' run_command(...) method.
        '''

        # TODO: build documentation
        if command == 'install_data':
            os.system("make -C doc")
        if command == 'clean':
            os.system("make -C doc clean")
        Distribution.run_command(self, command)

setup(name='flickrapi', 
    version=__version__, 
    url='http://flickrapi.sourceforge.net/', 
    author='Beej Jorgensen', 
    author_email='beej@beej.us', 
    maintainer='Sybren Stüvel',
    maintainer_email='sybren@stuvel.eu',
    description='Python interface to the Flickr API', 
    packages=['flickrapi'],
    data_files=[
        ('share/doc/flickrapi-%s' % __version__, ['doc/documentation.html', 'doc/documentation.css', 'doc/html4css1.css']),
    ],
    license='Python',
    distclass=OurDistribution
)
