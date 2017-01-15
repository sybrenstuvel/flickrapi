Changelog
=========

Version 2.2: in development
---------------------------

- Added this changelog file.
- Added explicit support for Python 3.5.
- Moved from a Mercurial repository at BitBucket to a Git repository
  at GitHub.
- Mocking some calls to Flickr, so that unit tests can run without
  requiring the user to authenticate via the browser. This also
  prevents the upload of the test photo.
- More serious testing, using py.test and Tox to test on all support
  versions of Python.
- Automated builds are performed with Travis-CI.
- Feature request #68: Make flickrapi token storage directory configurable.
- Alexandre L: Put requests in a session to benefit from connection reuse.
- When uploading a photo, send the title as UTF8
- Fixed issue #74 Sort many photosets with 'flickr.photosets.orderSets' failed.
- Michael Klich convert requested_permissions to unicode and ported authentication
  example to Python 3.
