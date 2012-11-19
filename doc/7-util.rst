
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

.. _flickr.photosets.getPhotos: http://www.flickr.com/services/api/flickr.photosets.getPhotos.html


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

.. _flickr.photos.search: http://www.flickr.com/services/api/flickr.photos.search.html


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
