
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
and is compatible with Python 2.7 and 3.4+.

Rendering the documentation requires `Sphinx <http://sphinx-doc.org/>`_.

.. _Requests: http://docs.python-requests.org/
.. _Six: http://packages.python.org/six/


Upgrading
----------------------------------------------------------------------

This section describes how to upgrade from older versions.

From 1.x to 2.0
+++++++++++++++++++++++++++++++++

For this release the main goal was to quickly transition from the obsolete
authentication method to OAuth. As a result, some features of the 1.x version
have been dropped. If you want any of those features back, let me know at:
https://bitbucket.org/sybren/flickrapi/issues?status=new&status=open


Authentication has been re-written to use OAuth. See the documentation
on how to use this. Some results are:

    - You always have to pass both the API key and secret. In 1.x you
      could choose to pass only the API key, but this no longer works
      with OAuth.

    - The token cache is now based on SQLite3, and contains not only
      the authentication tokens, but also the user's full name,
      username and NSID.

    - For non-web applications, a local HTTP server is started to
      receive the verification code. This means that the user does not
      have to copy and paste the verification code to the application.

    - The authentication callback functionality is gone. I'm not sure
      how many people still need this now that we've moved to OAuth.

    - The upload progress-callback functionality has been dropped. This was
      a hack on top of httplib, so this no longer works using Requests and
      OAuth.

    - Persistent connections have been dropped.

Flickr functions can be called with dotted notation. For example::

    flickr.photos_getInfo(photo_id='123') now becomes:
    flickr.photos.getInfo(photo_id='123')
                 ^
                 | note the change from underscore to dot.

For backward compatibility the old underscore-notation still works.


From 1.1
+++++++++++++++++++++++++++++++++

Some methods have been deprecated in version 1.1, which are now
removed. Those are the class methods:

    - test_failure
    - get_printable_error
    - get_rsp_error_code
    - get_rsp_error_msg

The default parser format has been changed from XMLNode to
ElementTree. Either convert your code to use the new ElementTree
parser, or pass the ``format='xmlnode'`` parameter to the FlickrAPI
constructor.

The upload and replace methods now use the format parameter, so if you
use ElementTree as the parser, you'll now also get an ElementTree
response from uploading and replacing photos. To keep the old
behaviour you can pass ``format='xmlnode'`` to those methods.

From 0.15
+++++++++++++++++++++++++++++++++

A lot of name changes have occurred in version 0.16 to follow PEP 8.
Some properties have also had their name shortened. For example, an
``XMLNode`` now has a ``text`` property instead of ``elementText``.
After all, the nodes describe XML elements, so what other text would
there be?

Here is a complete list of the publicly visible changes, broken down
per class. Changes in the internals of the FlickrAPI aren't documented
here.

``FlickrAPI``
    The constructor has its parameter ``apiKey`` changed to
    ``api_key``.

    All methods names that were originally in "camelCase" are now
    written in Python style. For example, ``getTokenPartOne`` has been
    changed to ``get_token_part_one``. The same is true for the class
    variables that point to the Flickr API URLs. For example,
    ``flickrHost`` became ``flickr_host``.

    ``send_multipart`` became a private method.

    The ``main`` method was removed. It only served as a simple
    example, which was obsoleted by the documentation.

``XMLNode``
    The method ``parseXML`` has become ``parse``, since it can't parse
    anything but XML, so there is no need to state the obvious.

    Properties ``elementName`` and ``elementText`` have been renamed
    to ``name`` resp. ``text``.

