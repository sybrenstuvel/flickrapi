#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''Python distutils install script.

Run with "python setup.py install" to install FlickrAPI
'''

from distutils.core import setup

from flickrapi import __version__

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
    license='Python'
)
