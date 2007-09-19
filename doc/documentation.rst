======================================================================
Python FlickrAPI
======================================================================

:Version: 0.14
:Author: Sybren Stüvel
:Status: Final

.. contents::
.. sectnum::

Introduction
======================================================================

`Flickr`_ is one of the most popular photo sharing websites. Their
public API makes it very easy to write applications that use Flickr
some way or another. The possibilities are limitless. This document
describes how to use the Flickr API in your Python programs using the
`Python Flickr API interface`_.


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


Authentication
======================================================================

Her photos may be private. Access to her account is private for sure.
A lot of Flickr API calls require the application to be authenticated.
This means that the user has to tell Flickr that the application is
allowed to do whatever it needs to do.

The Flickr document `User Authentication`_ explains the authentication
process; it's good to know what's in there before you go on.

The document states "The auth_token and api_sig parameters should then
be passed along with each request". You do *not* have to do this - the
Python Flickr API takes care of that.

Here is a simple example of Flickr's two-phase authentication::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = 'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)

    (token, frob) = flickr.getTokenPartOne(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.getTokenPartTwo((token, frob))

The ``api_key`` and ``api_secret`` can be obtained from
http://www.flickr.com/services/api/keys/.

The call to ``flickr.getTokenPartOne(...)`` does a lot of things.
First, it checks the on-disk token cache. After all, the application
may be authenticated already. 

If the application isn't authenticated, a browser opens the Flickr
page, on which the user can grant the application the appropriate
access. The application has to wait for the user to do this, hence the
``raw_input("Press ENTER after you authorized this program")``. A GUI
application can use a popup for this, or some other way for the user
to indicate she has performed the authentication ritual.

Once this step is done, we can continue to store the token in the
cache and remember it for future API calls. This is what
``flickr.getTokenPartTwo(...)`` does.



Calling API functions
======================================================================

When the application has been authenticated, the cool stuff can begin.
Calling a Flickr function is very easy. Here are some examples::

    untagged = flickr.photos_getUntagged(min_taken_date='2004-04-01')

    sets = flickr.photosets_getList()

There is a simple naming scheme here. If the flickr function is called
``flickr.photosets.getList`` just call ``photosets_getList`` on your
``flickr`` object. In other words: replace the dots with underscores.

Return values - XMLNodes
----------------------------------------------------------------------

Flickr sends back XML when you call a function. This XML is parsed
into ``XMLNode`` objects. Attributes in the XML are converted to
dictionary keys with unicode values. Subelements are stored in
properties.

Here is a simple example of the result of above ``sets =
flickr.photosets_getList()`` call.

Here is an example of an XML reply::

    <photosets cancreate="1">
        <photoset id="5" primary="2483" secret="abcdef" server="8" photos="4">
            <title>Test</title>
            <description>foo</description>
        </photoset>
        <photoset id="4" primary="1234" secret="832659" server="3" photos="12">
            <title>My Set</title>
            <description>bar</description>
        </photoset>
    </photosets>

The ``sets`` variable will be structured as such::

    sets['cancreate'] = u'1'
    sets.photoset = < a list of XMLNode objects >
    
    sets.photoset[0]['id'] = u'5'
    sets.photoset[0]['primary'] = u'2483'
    sets.photoset[0]['secret'] = u'abcdef'
    sets.photoset[0]['server'] = u'8'
    sets.photoset[0]['photos'] = u'4'
    sets.photoset[0].title[0].elementText = u'Test'
    sets.photoset[0].description[0].elementText = u'foo'
    
    sets.photoset[1]['id'] = u'4'
    sets.photoset[1]['primary'] = u'1234'
    sets.photoset[1]['secret'] = u'832659'
    sets.photoset[1]['server'] = u'3'
    sets.photoset[1]['photos'] = u'12'
    sets.photoset[1].title[0].elementText = u'My Set'
    sets.photoset[1].description[0].elementText = u'bar'

Every ``XMLNode`` also has a ``elementName`` property. The content of
this property is left as an exercise for the reader.

Future versions of the Python Flickr API might remove this ``XMLNode``
class and offer a DOM interface to the returned XML instead.

Erroneous calls
----------------------------------------------------------------------

When something has gone wrong Flickr will return an error code and a
description of the error. In this case, a ``FlickrError`` exception
will be thrown.

The old behaviour of the Python Flickr API was to simply return the
error code in the XML. However, this is deprecated behaviour as we
strive to notice an error condition as soon as possible. Checking the
return value of every call is not Pythonic. For backward compatibility
you can pass ``fail_on_error=False`` to the ``FlickrAPI`` constructor.

Other response formats
----------------------------------------------------------------------

Flickr supports different response formats, such as JSON and XML-RPC.
If you want, you can use such a different response format. Just
add a ``format="json"`` option to the Flickr call. The Python Flickr
API won't parse that format for you, though, so you just get the raw
response::

  >>> f.test_echo(boo='baah', format='json')
  'jsonFlickrApi({"format":{"_content":"json"},
    "auth_token":{"_content":"xxxxx"},
    "boo":{"_content":"baah"},
    "api_sig":{"_content":"xxx"},
    "api_key":{"_content":"xxx"},
    "method":{"_content":"flickr.test.echo"},
    "stat":"ok"})'

Uploading or replacing images
======================================================================

Transferring images requires special attention since they have to
send a lot of data. Therefore they also are a bit different than
advertised in the Flickr API documentation.

flickr.upload(...)
----------------------------------------------------------------------

The ``flickr.upload(...)`` method has the following parameters:

``filename``
    The filename of the image. The image data is read from this file.

``title``
    The title of the photo

``description``
    The description of the photo

``tags``
    Space-delimited list of tags. Tags that contain spaces need to be
    quoted. For example::

        tags='''Amsterdam "central station"'''

    Those are two tags, "Amsterdam" and "central station".

``is_public``
    "1" if the photo is public, "0" if it is private. The default is
    public.

``is_family``
    "1" if the private photo is visible for family, "0" if not. The
    default is not.

``is_friend``
    "1" if the private photo is visible for friends, "0" if not. The
    default is not.

``callback``
    This should be a method that receives two parameters, ``progress``
    and ``done``. The callback method will be called every once in a
    while during uploading. Example::

        def func(progress, done):
            if done:
                print "Done uploading"
            else:
                print "At %s%%" % progress

        flickr.upload(filename='test.jpg', callback=func)
    

flickr.replace(...)
----------------------------------------------------------------------

The ``flickr.replace(...)`` method has the following parameters:

``filename``
    The filename of the image.

``photo_id``
    The identifier of the photo that is to be replaced. Do not use
    this when uploading a new photo.

Only the image itself is replaced, not the other data (title, tags
etc.).

Unicode and UTF-8
======================================================================

Flickr expects every text to be encoded in UTF-8. The Python Flickr
API can help you in a limited way. If you pass a string as a
``unicode`` string, it will automatically be encoded to UTF-8 before
it's sent to Flickr.

If you do not use ``unicode`` strings, you're on your own, and you're
expected to perform the UTF-8 encoding yourself.

Here is an example::

    flickr.photos_setMeta(photo_id='12345',
                          title=u'Money',
                          description=u'Around \u20ac30,-')

This sets the photo's title to "Money" and the description to "Around
€30,-".

Requirements and compatibility
======================================================================

The Python Flickr API only uses built-in Python modules. It is
compatible with Python 2.5 and possibly earlier versions. We strive to
be compatible with older versions, but we have no tests for this yet.

Rendering the documentation requires `Docutils`_.

Links
======================================================================

- `Python Flickr API interface`_
- `Flickr`_
- `Flickr API documentation`_

.. _`Flickr API documentation`: http://www.flickr.com/services/api/
.. _`Flickr API`: http://www.flickr.com/services/api
.. _`Flickr`: http://www.flickr.com/
.. _`Python Flickr API interface`: http://flickrapi.sourceforge.net/
.. _`Docutils`: http://docutils.sourceforge.net/
.. _`User Authentication`:
    http://www.flickr.com/services/api/misc.userauth.html

