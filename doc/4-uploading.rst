
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
