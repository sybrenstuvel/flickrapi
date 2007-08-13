
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
    description='Python interface to the Flickr API', 
    py_modules=['flickrapi'])
