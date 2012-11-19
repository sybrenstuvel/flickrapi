
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

.. _`Django low-level cache API`: https://docs.djangoproject.com/en/dev/topics/cache/#the-low-level-cache-api
