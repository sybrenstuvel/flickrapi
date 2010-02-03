======================================================================
Python FlickrAPI
======================================================================

:Version: 1.4
:Author: Sybren Stüvel

.. contents::
.. sectnum::

Introduction
======================================================================

`Flickr`_ is one of the most popular photo sharing websites. Their
public API makes it very easy to write applications that use Flickr
some way or another. The possibilities are limitless. This document
describes how to use the Flickr API in your Python programs using the
`Python Flickr API interface`_.

This documentation does not specify what each Flickr API function
does, nor what it returns. The `Flickr API documentation`_ is the
source for that information, and will most likely be more up-to-date
than this document could be. Since the Python Flickr API uses dynamic
methods and introspection, you can call new Flickr methods as soon as
they become available.

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


Calling API functions
======================================================================

You start by creating a FlickrAPI object with your API key. This key
can be obtained at `Flickr Services`_. Once you have that key, the
cool stuff can begin. Calling a Flickr function is very easy. Here are
some examples::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    flickr = flickrapi.FlickrAPI(api_key)
    photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
    sets = flickr.photosets_getList(user_id='73509078@N00')

There is a simple naming scheme here. If the flickr function is called
``flickr.photosets.getList`` just call ``photosets_getList`` on your
``flickr`` object. In other words: replace the dots with underscores.

Parsing the return value
----------------------------------------------------------------------

Flickr sends back XML when you call a function. This XML is parsed and
returned to you. There are two parsers available: ElementTree and
XMLNode. ElementTree was introduced in version 1.1, and replaced
XMLNode as the default parser as of version 1.2.

In the following sections, we'll use a ``sets =
flickr.photosets_getList(...)`` call and assume this was the response
XML::

    <rsp stat='ok'>
        <photosets cancreate="1">
            <photoset id="5" primary="2483" secret="abcdef"
                    server="8" photos="4">
                <title>Test</title>
                <description>foo</description>
            </photoset>
            <photoset id="4" primary="1234" secret="832659"
                    server="3" photos="12">
                <title>My Set</title>
                <description>bar</description>
            </photoset>
        </photosets>
    </rsp>

Response parser: ElementTree
----------------------------------------------------------------------

The old XMLNode parser had some drawbacks. A better one is Python's
standard ElementTree_. If you create the ``FlickrAPI`` instance like
this, you'll use ElementTree::

    flickr = flickrapi.FlickrAPI(api_key)

or explicitly::

    flickr = flickrapi.FlickrAPI(api_key, format='etree')

The `ElementTree documentation`_ is quite clear, but to make things
even easier, here are some examples using the same call and response
XML as in the XMLNode example::

    sets = flickr.photosets_getList(user_id='73509078@N00')

    sets.attrib['stat'] => 'ok'
    sets.find('photosets').attrib['cancreate'] => '1'

    set0 = sets.find('photosets').findall('photoset')[0]

    +-------------------------------+-----------+
    | variable                      | value     |
    +-------------------------------+-----------+
    | set0.attrib['id']             | u'5'      |
    | set0.attrib['primary']        | u'2483'   |
    | set0.attrib['secret']         | u'abcdef' |
    | set0.attrib['server']         | u'8'      |
    | set0.attrib['photos']         | u'4'      |
    | set0.title[0].text            | u'Test'   |
    | set0.description[0].text      | u'foo'    |
    | set0.find('title').text       | 'Test'    |
    | set0.find('description').text | 'foo'     |
    +-------------------------------+-----------+

    ... and similar for set1 ...

ElementTree is a more mature, better thought out XML parsing
framework. It has several advantages over the old XMLNode parser:

    #. As a standard XML representation, ElementTree will be easier to
       plug into existing software.

    #. Easier to iterate over elements. For example, to list all
       "title" elements, you only need to do
       ``sets.getiterator('title')``.

    #. Developed by the Python team, which means it's subject to more
       rigorous testing and has a wider audience than the Python
       Flickr API module. This will result in a higher quality and
       less bugs.

ElementTree in Python 2.4
----------------------------------------------------------------------

Python 2.5 comes shipped with ElementTree. To get it running on Python
2.4 you'll have to install ElementTree yourself. The easiest way is to
get setuptools and then just type::

    easy_install elementtree
    easy_install flickrapi

That'll get you both ElementTree and the latest version of the Python
Flickr API.

Another method is to get the Python FlickrAPI source and run::

    python setup.py install
    easy_install elementtree

As a last resort, you can `download ElementTree`_ and install it
manually.

Response parser: XMLNode
----------------------------------------------------------------------

The XMLNode objects are quite simple. Attributes in the XML are
converted to dictionary keys with unicode values. Subelements are
stored in properties.

We assume you did ``sets = flickr.photosets_getList(...)``. The
``sets`` variable will be structured as such::

    sets['stat'] = 'ok'
    sets.photosets[0]['cancreate'] = u'1'
    sets.photosets[0].photoset = < a list of XMLNode objects >

    set0 = sets.photosets[0].photoset[0]
    set1 = sets.photosets[0].photoset[1]

    +--------------------------+-----------+
    | variable                 | value     |
    +--------------------------+-----------+
    | set0['id']               | u'5'      |
    | set0['primary']          | u'2483'   |
    | set0['secret']           | u'abcdef' |
    | set0['server']           | u'8'      |
    | set0['photos']           | u'4'      |
    | set0.title[0].text       | u'Test'   |
    | set0.description[0].text | u'foo'    |
    +--------------------------+-----------+
    | set1['id']               | u'4'      |
    | set1['primary']          | u'1234'   |
    | set1['secret']           | u'832659' |
    | set1['server']           | u'3'      |
    | set1['photos']           | u'12'     |
    | set1.title[0].text       | u'My Set' |
    | set1.description[0].text | u'bar'    |
    +--------------------------+-----------+

Every ``XMLNode`` also has a ``name`` property. The content of this
property is left as an exercise for the reader.

As of version 1.2 of the Python Flickr API this XMLNode parser is no
longer the default parser, in favour of the ElementTree parser.
XMLNode is still supported, though.

Erroneous calls
----------------------------------------------------------------------

When something has gone wrong Flickr will return an error code and a
description of the error. In this case, a ``FlickrError`` exception
will be thrown.

The old behaviour of the Python Flickr API was to simply return the
error code in the XML not raising any exception. It was possible to
pass ``fail_on_error=False`` to the ``FlickrAPI`` constructor to get
this behaviour, but this was deprecated in version 1.1 and has been
removed in version 1.3.

Unparsed response formats
----------------------------------------------------------------------

Flickr supports different response formats, such as JSON and XML-RPC.
If you want, you can use such a different response format. Just add a
``format="json"`` option to the Flickr call. The Python Flickr API
won't parse that format for you, though, so you just get the raw
response::

  >>> f = flickrapi.FlickrAPI(api_key)
  >>> f.test_echo(boo='baah', format='json')
  'jsonFlickrApi({"format":{"_content":"json"},
    "auth_token":{"_content":"xxxxx"},
    "boo":{"_content":"baah"},
    "api_sig":{"_content":"xxx"},
    "api_key":{"_content":"xxx"},
    "method":{"_content":"flickr.test.echo"},
    "stat":"ok"})'

If you want all your calls in a certain format, you can also use the
``format`` constructor parameter::

  >>> f = flickrapi.FlickrAPI(api_key, format='json')
  >>> f.test_echo(boo='baah')
  'jsonFlickrApi({"format":{"_content":"json"},
    "auth_token":{"_content":"xxxxx"},
    "boo":{"_content":"baah"},
    "api_sig":{"_content":"xxx"},
    "api_key":{"_content":"xxx"},
    "method":{"_content":"flickr.test.echo"},
    "stat":"ok"})'

If you use an unparsed format, FlickrAPI won't check for errors. Any
format not described in the "Response parser" sections is considered
to be unparsed.

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

    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

The ``api_key`` and ``api_secret`` can be obtained from
http://www.flickr.com/services/api/keys/.

The call to ``flickr.get_token_part_one(...)`` does a lot of things.
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
``flickr.get_token_part_two(...)`` does.

Authentication callback
----------------------------------------------------------------------

By default a webbrowser is started to let the user perform the
authentication. However, this may not be appropriate or even possible
in your application. If you want to alter this functionality, use the
``auth_callback`` parameter when calling ``get_token_part_one(...)``.
The function will be passed the frob and the requested permission::

    def auth(frob, perms):
        print 'Please give us permission %s' % perms

    (token, frob) = flickr.get_token_part_one(perms='write', auth)

Of course this example isn't useful, but it shows how to use the
callback. If you just want to wrap the browser startup with some code,
call ``flickr.validate_frob(frob, perms)`` from your callback.

Authenticating web applications
----------------------------------------------------------------------

When working with web applications, things are a bit different. The
user using the application (through a browser) is likely to be
different from the user running the server-side software.

We'll assume you're following Flickr's `Web Applications How-To`_, and
just tell you how things are splified when working with the Python
Flickr API.

    3. Create a login link. Use ``flickr.web_login_url(perms)``` for
       that.  It'll return the login link for you, given the
       permissions you passed in the ``perms`` parameter.

    5. Don't bother understanding the signing process; the
       ``FlickrAPI`` module takes care of that for you. Once you
       received the frob from Flickr, use
       ``flickr.get_token("the_frob")``. The FlickrAPI module will
       remember the token for you.

    6. You can safely skip this, and just use the FlickrAPI module as
       usual. Only read this if you want to understand how the
       FlickrAPI module signs method calls for you.

Token handling in web applications
----------------------------------------------------------------------

Web applications have two kinds of users: identified and anonymous
users. If your users are identified, you can pass their name (or other
means of identification) as the ``username`` parameter to the
``FlickrAPI`` constructor, and get a FlickrAPI instance that's bound
to that user. It will keep track of the authentication token for that
user, and there's nothing special you'll have to do.

When working with anonymous users, you'll have to store the
authentication token in a cookie. In step 5. above, use this::

    token = flickr.get_token("the_frob")

Then use your web framework to store the token in a cookie. When
reading a token from a cookie, pass it on to the FlickrAPI constructor
like this::

    flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)

It won't be stored in the on-disk token cache - which is a good thing,
since

    A. you don't know who the user is, so you wouldn't be able to
       retrieve the appropriate tokens for visiting users.

    B. the tokens are stored in cookies, so there is no need to store
       them in another place.

Preventing usage of on-disk token cache
----------------------------------------------------------------------

Another way of preventing the storage of tokens is to pass
``store_token=False`` as the constructor parameter. Use this if you
want to be absolutely sure that the FlickrAPI instance doesn't use any
previously stored tokens, nor that it will store new tokens.

Controlling the location of the on-disk token cache
----------------------------------------------------------------------

By default the authentication tokens are stored in the directory
``~/.flickr``. If you want to change this directory, you can do so
by changing the ``flickr.token.path`` variable after you have created
the ``FlickrAPI`` instance::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = 'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.token.path = '/tmp/flickrtokens'

    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))
 
Multiple processes using the same key
----------------------------------------------------------------------

By default the token is stored on the filesystem in
``somepath/<authentication key>/auth.token``. When multiple
processes use the same authentication key a race condition can occur
where the authentication token is removed. To circumvent this, use the
``LockingTokenCache`` instead::

    from flickrapi import FlickrAPI
    from flickrapi.tokencache import LockingTokenCache
    
    flickr = flickrapi.FlickrAPI(api_key, secret)
    
    flickr.token_cache = LockingTokenCache(api_key)
    # -- or --
    flickr.token_cache = LockingTokenCache(api_key, username)

This cache ensures that only one process at the time can use the token
cache. It does not forsee in multi-threading.

As the locking mechanism causes additional disk I/O and performs more
checks, it is slower than the regular cache. Since not that many
people use the same key in parallel on one machine (or a shared
filesystem on which the token is stored) the default token cache does
not use locking.

Example using Django
----------------------------------------------------------------------

Here is a simple example in Django_::

 import flickrapi
 from django.conf import settings
 from django.http import HttpResponseRedirect, HttpResponse

 import logging
 logging.basicConfig()

 log = logging.getLogger(__name__)
 log.setLevel(logging.DEBUG)

 def require_flickr_auth(view):
     '''View decorator, redirects users to Flickr when no valid
     authentication token is available.
     '''

     def protected_view(request, *args, **kwargs):
         if 'token' in request.session:
             token = request.session['token']
             log.info('Getting token from session: %s' % token)
         else:
             token = None
             log.info('No token in session')

        f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY,
                settings.FLICKR_API_SECRET, token=token,
                store_token=False)

         if token:
             # We have a token, but it might not be valid
             log.info('Verifying token')
             try:
                 f.auth_checkToken() 
             except flickrapi.FlickrError:
                 token = None 
                 del request.session['token']

         if not token:
             # No valid token, so redirect to Flickr
             log.info('Redirecting user to Flickr to get frob')
             url = f.web_login_url(perms='read')
             return HttpResponseRedirect(url)

         # If the token is valid, we can call the decorated view.
         log.info('Token is valid')
         
         return view(request, *args, **kwargs)

     return protected_view

 def callback(request):
     log.info('We got a callback from Flickr, store the token')

    f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY,
            settings.FLICKR_API_SECRET, store_token=False)

     frob = request.GET['frob']
     token = f.get_token(frob)
     request.session['token'] = token

     return HttpResponseRedirect('/content')

 @require_flickr_auth
 def content(request):
     return HttpResponse('Welcome, oh authenticated user!')

Every view that calls an authenticated Flickr method should be
decorated with ``@require_flickr_auth``. For more information on
function decorators, see `PEP 318`_.

The ``callback`` view should be called when the user is sent to the
callback URL as defined in your Flickr API key. The key and secret
should be configured in your settings.py, in the properties
``FLICKR_API_KEY`` and ``FLICKR_API_SECRET``.

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
``format``
    The response format. This *must* be either ``rest`` or one of the
    parsed formats ``etree`` / ``xmlnode``.

flickr.replace(...)
----------------------------------------------------------------------

The ``flickr.replace(...)`` method has the following parameters:

``filename``
    The filename of the image.

``photo_id``
    The identifier of the photo that is to be replaced. Do not use
    this when uploading a new photo.

``format``
    The response format. This *must* be either ``rest`` or one of the
    parsed formats ``etree`` / ``xmlnode``.

Only the image itself is replaced, not the other data (title, tags,
comments, etc.).

Unicode and UTF-8
======================================================================

Flickr expects every text to be encoded in UTF-8. The Python Flickr
API can help you in a limited way. If you pass a ``unicode`` string,
it will automatically be encoded to UTF-8 before it's sent to Flickr.
This is the preferred way of working, and is also forward-compatible
with the upcoming Python 3.

If you do not use ``unicode`` strings, you're on your own, and you're
expected to perform the UTF-8 encoding yourself.

Here is an example::

    flickr.photos_setMeta(photo_id='12345',
                          title=u'Money',
                          description=u'Around \u20ac30,-')

This sets the photo's title to "Money" and the description to "Around
€30,-".

Caching of Flickr API calls
======================================================================

There are situations where you call the same Flickr API methods over
and over again. An example is a web page that shows your latest ten
sets. In those cases caching can significantly improve performance.

The FlickrAPI module comes with its own in-memory caching framework.
By default it caches at most 200 entries, which time out after 5
minutes. These defaults are probably fine for average use. To use the
cache, just pass ``cache=True`` to the constructor::

    flickr = flickrapi.FlickrAPI(api_key, cache=True)

To tweak the cache, instantiate your own instance and pass it some
constructor arguments::

    flickr = flickrapi.FlickrAPI(api_key, cache=True)
    flickr.cache = flickrapi.SimpleCache(timeout=300, max_entries=200)

``timeout`` is in seconds, ``max_entries`` in number of cached
entries.

Using the Django caching framework
----------------------------------------------------------------------

The caching framework was designed to have the same interface as the
`Django low-level cache API`_ - thanks to those guys for designing a
simple and effective cache. The result is that you can simply plug the
Django caching framework into FlickrAPI, like this::
    
    from django.core.cache import cache
    flickr = flickrapi.FlickrAPI(api_key, cache=True)
    flickr.cache = cache

That's all you need to enable a wealth of caching options, from
database-backed cache to multi-node in-memory cache farms.

Utility methods
======================================================================

There are a couple of useful methods for handling photos.

*All utility methods require ElementTree to be available, so either
use Python 2.5 or newer, or install it as described above.*

Walking through all photos in a set
----------------------------------------------------------------------

It may be useful to be able to easily perform an operation on every
photo in a set. This is what the ``walk_set`` function does. It
accepts a photoset ID and returns a generator::

    flickr = flickrapi.FlickrAPI(api_key)
    for photo in flickr.walk_set('2b640a3efc262f03567ee93cfd544e14'):
        print photo.get('title')

The function uses the Flickr API call flickr.photosets.getPhotos_ and
accepts the same parameters. The resulting "photo" objects are
ElementTree objects for the ``<photo .../>`` XML elements.

Walking through a search result
----------------------------------------------------------------------

Walking through a search result is done in much the same way as
walking through all photos in a set::

    flickr = flickrapi.FlickrAPI(api_key)
    for photo in flickr.walk(tag_mode='all',
            tags='sybren,365,threesixtyfive',
            min_taken_date='2008-08-20',
            max_taken_date='2008-08-30'):
        print photo.get('title')

The function uses the Flickr API call flickr.photos.search_ and
accepts the same parameters. The resulting "photo" objects are
ElementTree objects for the ``<photo .../>`` XML elements.

Influencing the number of calls to Flickr
----------------------------------------------------------------------

The walking functions described above only call Flickr when they have
to. When they do, they fetch ``per_page`` (default 50) photos
simultaneously. The ``per_page`` parameter can be used to tweak the
number of calls. The following will perform two calls two Flickr::

    flickr = flickrapi.FlickrAPI(api_key)
    set = flickr.walk_set('<set id>', per_page=15)
    for photo in set[:25]:
        print photo.get('title')

The first call will get photos 0-14, the next call will get 15-29,
even though only the first 25 photo titles will be shown.

Another example, if you only want to show the titles of photos 5-20::

    flickr = flickrapi.FlickrAPI(api_key)
    set = flickr.walk_set('<set id>' per_page=20)
    for photo in set[5:21]:
        print photo.get('title')

The photos will always be fetched from the first page onwards. In the
above example, the first twenty photos will all be fetched, even
though the title of the first five will be skipped.

Short Flickr URLs
======================================================================

Flickr supports linking to a photo page using a short url such as
`http://flic.kr/p/6BTTT6`_. The ``flickrapi.shorturl`` module contains
functionality for working with those short URLs.

``flickrapi.shorturl.encode(photo ID)``:
    Returns the short ID for this photo ID

``flickrapi.shorturl.encode(short ID)``:
    Returns the photo ID for this short ID

``flickrapi.shorturl.url(photo ID)``:
    Returns the short URL for the given photo ID.

The photo ID, the short ID and the short URL are all unicode strings.


Requirements and compatibility
======================================================================

The Python Flickr API only uses built-in Python modules. It is
compatible with Python 2.4 and newer.

Usage of the "etree" format requires Python 2.5 or newer.

Rendering the documentation requires `Docutils`_.

Links
======================================================================

- `Python Flickr API interface`_
- `Flickr`_
- `Flickr API documentation`_

.. _`Flickr Services`: http://www.flickr.com/services/api/keys/apply/
.. _`Flickr API documentation`: http://www.flickr.com/services/api/
.. _`Flickr API`: http://www.flickr.com/services/api
.. _`Flickr`: http://www.flickr.com/
.. _`Python Flickr API interface`: http://www.stuvel.eu/projects/flickrapi
.. _`Docutils`: http://docutils.sourceforge.net/
.. _`User Authentication`:
    http://www.flickr.com/services/api/misc.userauth.html
.. _`Web Applications How-To`:
    http://www.flickr.com/services/api/auth.howto.web.html
.. _Django: http://www.djangoproject.com/
.. _`PEP 318`: http://www.python.org/dev/peps/pep-0318/
.. _`ElementTree`: http://docs.python.org/lib/module-xml.etree.ElementTree.html
.. _`ElementTree documentation`: http://docs.python.org/lib/module-xml.etree.ElementTree.html
.. _`Django low-level cache API`: http://www.djangoproject.com/documentation/cache/#the-low-level-cache-api
.. _`download ElementTree`: http://effbot.org/downloads/#elementtree

.. _flickr.photosets.getPhotos: http://www.flickr.com/services/api/flickr.photosets.getPhotos.html
.. _flickr.photos.search: http://www.flickr.com/services/api/flickr.photos.search.html
.. _`http://flic.kr/p/6BTTT6`: http://flic.kr/p/6BTTT6
