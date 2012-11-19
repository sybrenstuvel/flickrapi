
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

    flickr.photos.setMeta(photo_id='12345',
                          title=u'Money',
                          description=u'Around \u20ac30,-')

This sets the photo's title to "Money" and the description to "Around
€30,-".
