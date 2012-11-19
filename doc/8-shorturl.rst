
Short Flickr URLs
======================================================================

Flickr supports linking to a photo page using a short url such as
http://flic.kr/p/6BTTT6. The ``flickrapi.shorturl`` module contains
functionality for working with those short URLs.

``flickrapi.shorturl.encode(photo ID)``:
    Returns the short ID for this photo ID

``flickrapi.shorturl.encode(short ID)``:
    Returns the photo ID for this short ID

``flickrapi.shorturl.url(photo ID)``:
    Returns the short URL for the given photo ID.

The photo ID, the short ID and the short URL are all unicode strings.
