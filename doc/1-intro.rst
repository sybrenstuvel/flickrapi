
Introduction
======================================================================

This documentation does not specify what each Flickr API function
does, nor what it returns. The `Flickr API documentation`_ is the
source for that information, and will most likely be more up-to-date
than this document could be. Since the Python Flickr API uses dynamic
methods and introspection, you can call new Flickr methods as soon as
they become available.

.. _`Flickr API documentation`: http://www.flickr.com/services/api/
.. _`Flickr`: http://www.flickr.com/
.. _`Python Flickr API interface`: http://stuvel.eu/flickrapi


Concepts
----------------------------------------------------------------------

To keep things simple, we do not write "he/she" or "(s)he". We know
that men and women can all be fine programmers and end users. Some
people will be addressed as male, others as female.

To be able to easily talk about Flickr, its users, programmers and
applications, here is an explanation of some concepts we use.


you
    The reader of this document. We assume you are a programmer and
    that you are using this Python Flickr API to create an
    application. In this document we shall address you as male.

application
    The Python application you are creating, that has to interface
    with Flickr.

user
    The user of the application, and thus (either directly or
    indirectly via your application) a Flickr user. In this document
    we shall address the user as female.

Installation
----------------------------------------------------------------------

You can install Python FlickrAPI from the Python Package Index using::

 pip install flickrapi

Installation from source is done using::

 python setup.py install

Developers of the Python Flickr API code (that is, people working on the
library code, rather than using the library) can install development
dependencies using::

 pip install -r requirements.txt


Requirements and compatibility
----------------------------------------------------------------------

The Python Flickr API uses two external libraries, Requests_ and Six_,
and is compatible with Python 2.6 and 2.7. As of this moment Requests
has (at least) one `bug <https://github.com/kennethreitz/requests/issues/944>`_
that makes it incompatible with Python 3.2. When that is fixed, we will
make Python Flick API compatible with Python 3.2+ too.

Rendering the documentation requires `Sphinx <http://sphinx-doc.org/>`_.

.. _Requests: http://docs.python-requests.org/
.. _Six: http://packages.python.org/six/


