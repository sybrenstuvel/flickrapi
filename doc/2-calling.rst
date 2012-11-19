
Calling API functions
======================================================================

You start by creating a FlickrAPI object with your API key and secret.
These can be obtained at `Flickr Services`_. Once you have that key, the
cool stuff can begin. Calling a Flickr function is very easy. Here are
some examples::

    import flickrapi

    api_key = u'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = u'YYYYYYYYYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    photos = flickr.photos.search(user_id='73509078@N00', per_page='10')
    sets = flickr.photosets.getList(user_id='73509078@N00')

.. _`Flickr Services`: http://www.flickr.com/services/api/keys/apply/

The API key and secret MUST be Unicode strings. All parameters you pass
to Flickr MUST be passed as keyword arguments.

Parsing the return value
----------------------------------------------------------------------

Flickr sends back XML when you call a function. This XML is parsed and
returned to the application. There are two parsers available: ElementTree and
XMLNode. ElementTree was introduced in Python Flickr API version 1.1, and replaced
XMLNode as the default parser as of version 1.2. If you want another format,
such as JSON, you can use that too - see `Unparsed response formats`_.

In the following sections, we'll use a ``sets =
flickr.photosets.getList(...)`` call and assume this was the response
XML:

.. code-block:: xml

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

ElementTree_ is an XML parser library that's part of Python's standard
library. It is the default response parser, so if you create the ``FlickrAPI``
instance like this, you'll use ElementTree::

    flickr = flickrapi.FlickrAPI(api_key, api_secret)

or explicitly::

    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='etree')

The ElementTree_ documentation is quite clear, but to make things
even easier, here are some examples using the call and response
XML as described above::

    sets = flickr.photosets.getList(user_id='73509078@N00')

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

.. _ElementTree: http://effbot.org/zone/element.htm

Response parser: XMLNode
----------------------------------------------------------------------

The XMLNode objects are quite simple. Attributes in the XML are
converted to dictionary keys with unicode values. Subelements are
stored in properties.

We assume you did ``sets = flickr.photosets.getList(...)``. The
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

Unparsed response formats
----------------------------------------------------------------------

Flickr supports different response formats, such as JSON and SOAP.
If you want, you can use such a different response format. Just add a
parameter like ``format="json"`` to the Flickr call. The Python Flickr API
won't parse that format for you, and you just get the raw response::

  >>> f = flickrapi.FlickrAPI(api_key, api_secret)
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

  >>> f = flickrapi.FlickrAPI(api_key, api_secret, format='json')
  >>> f.test.echo(boo='baah')
  'jsonFlickrApi({"format":{"_content":"json"},
    "auth_token":{"_content":"xxxxx"},
    "boo":{"_content":"baah"},
    "api_sig":{"_content":"xxx"},
    "api_key":{"_content":"xxx"},
    "method":{"_content":"flickr.test.echo"},
    "stat":"ok"})'

If you use an unparsed format, FlickrAPI won't check for errors. Any
format supported by Flickr but not described in the "Response parser"
sections is considered to be unparsed.
