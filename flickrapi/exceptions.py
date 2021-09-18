"""Exceptions used by the FlickrAPI module."""


class IllegalArgumentException(ValueError):
    """Raised when a method is passed an illegal argument.

    More specific details will be included in the exception message
    when thrown.
    """


class FlickrError(Exception):
    """Raised when a Flickr method fails.

    More specific details will be included in the exception message
    when thrown.
    """

    def __init__(self, message, code=None):
        Exception.__init__(self, message)

        if code is None:
            self.code = None
        else:
            self.code = int(code)


class FlickrDuplicate(Exception):
    """Raised when Flickr detects duplicate photo being uploaded.

    The duplicate detection only happens if the upload request contains
    the 'dedup_check' parameter set to either 1 or 2.

    The exception contains ID of the duplicate photo as returned
    from the API call.

    """
    def __init__(self, message, duplicate_photo_id):
        super().__init__(self, message)

        self.duplicate_photo_id = duplicate_photo_id


class CancelUpload(Exception):
    """Raise this exception in an upload/replace callback function to
    abort the upload.
    """


class LockingError(Exception):
    """Raised when TokenCache cannot acquire a lock within the timeout
    period, or when a lock release is attempted when the lock does not
    belong to this process.
    """


class CacheDatabaseError(FlickrError):
    """Raised when the OAuth token cache database is corrupted
    or otherwise unusable.
    """
