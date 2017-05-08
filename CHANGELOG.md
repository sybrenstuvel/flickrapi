Python FlickrAPI Changelog
==========================

This is the changelog of the Python FlickrAPI package. All changes were made by
Sybren A. Stüvel, unless noted otherwise.


Version 2.3: released 2017-05-08
--------------------------------

- Include README.md and CHANGELOG.md in the package data.
- Removed flickrapi/contrib.py, as a persistent connection is now managed (much better)
  by requests (since [cdeb6ffea26](https://github.com/sybrenstuvel/flickrapi/commit/cdeb6ffea26)).
- Late-import module `webbrowser`, only when needed (Thijs Triemstra)
  [[ Pull request #78 ]](https://github.com/sybrenstuvel/flickrapi/pull/78)
- Perform explicit commit after inserting auth token (Joshua Hunter)
  [[ Bug report #75 ]](https://github.com/sybrenstuvel/flickrapi/pull/75)
  [[ Pull request #76 ]](https://github.com/sybrenstuvel/flickrapi/pull/76)
- Configured Tox & Travis to test on Python 3.6 as well.
- Timeout for API calls.
  [[ Feature Request #27 ]](https://github.com/sybrenstuvel/flickrapi/issues/27)
- Late-import SQLite3 to allow running on Heroku (and other systems).
  [[ Feature Request #81 ]](https://github.com/sybrenstuvel/flickrapi/issues/81)
- Fixed using obsolete `func_name` attribute.
  [[ Bug report #80 ]](https://github.com/sybrenstuvel/flickrapi/issues/80)


Version 2.2.1: released 2017-01-15
----------------------------------

- Converted the old changelog (on [stuvel.eu](https://stuvel.eu/flickrapi/changelog))
  from HTML to MarkDown, and added that to this file.
- Added some missing changes to the version 2.2 section.


Version 2.2: released 2017-01-15
--------------------------------

- Added this changelog file.
- Added explicit support for Python 3.5.
- Moved from a Mercurial repository at BitBucket to a [Git repository
  at GitHub](https://github.com/sybrenstuvel/flickrapi/).
- Mocking some calls to Flickr, so that unit tests can run without
  requiring the user to authenticate via the browser. This also
  prevents the upload of the test photo.
- More serious testing, using py.test and Tox to test on all support
  versions of Python.
- Automated builds are performed with Travis-CI.
- Make flickrapi token storage directory configurable.
  [[ Feature request #68 ]](https://github.com/sybrenstuvel/flickrapi/issues/68)
- Put requests in a session to benefit from connection reuse (Alexandre L).
- When uploading a photo, send the title as UTF8
- Sort many photosets with 'flickr.photosets.orderSets' failed
  [[ Bug report #74]](https://github.com/sybrenstuvel/flickrapi/issues/74)
- Converted requested_permissions to unicode and ported authentication
  example to Python 3 (Michael Klich).


Version 2.1.2: released 2015-10-27
----------------------------------

- Added error checking (and raising of `FlickrError`) from the parsed-json handler


Version 2.1.1: released 2015-08-03
----------------------------------

- Bumped version to 2.1.1 due to some mistake with pypi


Version 2.1: released 2015-08-03
--------------------------------

- solved issue with `autenticate_console()` [[ Bug report #58 ]](https://github.com/sybrenstuvel/flickrapi/issues/58)
- Using POST instead of GET [[ Bug report #59 ]](https://github.com/sybrenstuvel/flickrapi/issues/59)
- Fix: use req.text for text-based interpretation of HTTP response.


Version 2.0.1: released 2014-12-18
----------------------------------

- Lowered dependency versions to those shipped with Ubuntu 14.04 LTS
- Added Python 3.3 to the list of supported versions, rejecting Python <=2.6 and <=3.2.
- Allow non-ascii characters in file names (Jim Easterbrook)


Version 2.0: released 2014-11-06
--------------------------------

- Major revision; now uses OAuth to interface with
  Flickr. Combines work of Sybren A. Stüvel, Jim Easterbrook,
  Thai Nguyen, Nick Loadholtes and Bengt.


Version 1.4.4: released 2014-06-18
--------------------------------

- Changed default API URL to use HTTPS (Joseph Hui).
- PEP 8 compliance (Luar Roji).
- Replaced Distribute with Setuptools.


Versions 1.4.1 .. 1.4.3: unreleased
-----------------------------------

- Lots of messy changes to smoothen release procedure.

Version 1.4: released 2010-02-03
--------------------------------

- Using `auth_callback=False` when authentication
  is actually required now raises a `FlickrError`
  exception.

- The implementation uses `self.flickr_host`
  that subclasses can override the API URLs.

- Support for short URLs was added.


Version 1.3: released 2009-10-03
--------------------------------

- Added functions to easily walk through sets and search
  results, querying Flickr no more than needed.
- Uses the hashlib module, falling back to the md5 module
  when hashlib is unavailable.
- Added locking token cache, in case a Flickr API key is
  used by multiple processes at the same time on the same
  machine (or shared filesystem)
- Removed the deprecated `fail_on_error` parameter.
- Implemented the `auth_callback` functionality.


Version 1.2: released 2008-11-15
--------------------------------

- Added ElementTree support for Python 2.4.
  [[ Patch 2007996 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=2007996&group_id=203043&atid=984008)
- Made ElementTree the default response parser.
- The upload and replace methods now take a `format` parameter.
  [[ Feature request 1912606 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1912606&group_id=203043&atid=984009)
- Removed deprecated methods.
- `upload` and `replace` methods no longer report progress on their callback
  regarding the HTTP headers.


Version 1.1: released 2008-04-15
--------------------------------

- Tab completion of all Flickr API functions in IPython.
- Fix for a bug where a crash occurred when XML containing
  a `<name />` element was parsed with XMLNode.
- Deprecated a number of methods for old-style error handling, including the
  `fail_on_error` constructor parameter. Just handle the `FlickrError` exceptions
  instead of explicitly testing all method calls. The deprecated methods will be
  completely removed in release 1.2.
- Implemented a response parser system, which still parses to XMLNode objects by
  default. It now also includes parsing to the Python standard ElementTree, which will
  soon replace XMLNode as the default response parser. See the
  [documentation](http://flickrapi.sf.net/flickrapi.html) on how to use the new parsers.
- Added `format` constructor parameter to set the default response format for all
  method calls. Overriding per call is still possible.
- Added `store_token` constructor parameter that's `True` by
  default. Set to `False` to ensure the on-disk token cache isn't
  used. [[ Feature request 1923728 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1923728&group_id=203043&atid=984009)
- Added caching framework. Pass `cache=True` to the constructor to
  use it. [[ Feature request 1911450 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1911450&group_id=203043&atid=984009)


Version 1.0: released 2008-03-12
--------------------------------

- Added [API documentation](http://flickrapi.sf.net/apidoc/). [[ Feature request 1834460 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1834460&group_id=203043&atid=984009)

- Lot of code improvements, most of them renaming of the public
  interface to the Python coding standard described in PEP 8. The
  exact publicly visible changes are described in the UPGRADING file.
  [[ Feature request 1773473 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1773473&group_id=203043&atid=984009)
- Added multi-user support to the authentication token cache.
  [[ Feature request 1874067 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1874067&group_id=203043&atid=984009)
- Support for web applications.
  [[ Feature request 1896701 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1896701&group_id=203043&atid=984009)
- Passing `format='rest'` results in unparsed XML from the REST
  request. [[ Feature request 1834459 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1834459&group_id=203043&atid=984009)
- Removed `uuid` module and replaced it with our own random MIME boundary generator.
- Improved code and package documentation.


Version 0.15: released 2007-11-07
--------------------------------

- Support for unauthenticated, read-only access to the Flickr API.
  [[ Feature request 1802210 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1802210&group_id=203043&atid=984009)
- Deprecated the `getToken(...)` method. Use
  `getTokenPartOne(...)` and `getTokenPartTwo(...)` instead.
- Better Windows compatibility by opening JPEG files in binary mode.


Version 0.14: released 2007-09-19
--------------------------------

- `upload` method allows for the application to receive progress
  information regarding running uploads.
  [[ Feature request 1793276 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1793276&group_id=203043&atid=984009)

- Preliminary support for different response formats. If a format
  other than the default REST is chosen, the raw response will be
  returned to the caller without parsing.
- Python 2.4 compatibility.
- Uses the `webbrowser` Python module to start a webbrowser, instead
  of doing it ourselves. This will greatly improve the platform
  independence of applications.
  [[ Feature request 1793350 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1793350&group_id=203043&atid=984009)

  Please note that this changes the API itself - you can no longer
  pass the 'browser' and 'fork' parameters to the `getTokenPartOne(...)`
  method call. The `webbrowser` module figures out what to do by
  itself.


Version 0.13: released 2007-09-12
--------------------------------

- No longer allow passing `jpegData` to the `upload` or
  `replace` methods. The code handling it was buggy. If you're
  actually using the `jpegData` parameter of those functions, let us
  know and we might restore the functionality in a proper way.
- Full Unicode compatibility. Pass strings as `unicode` objects, and
  they'll be automatically encoded as UTF-8 before sending to Flickr.
  [[ Bug report 1779463 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1779463&group_id=203043&atid=984006)
- Introduced unittests. Not everything is covered yet, but we've got a
  good start.
  [[ Feature request 1773475 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1773475&group_id=203043&atid=984009)
- Refactored the upload/replace methods.
  [[ Feature request 1778905 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1778905&group_id=203043&atid=984009)
- Gracefully handle corrupt or otherwise invalid data in the token
  cache.
  [[ Feature request 1781236 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1781236&group_id=203043&atid=984009)


Version 0.12: released 2007-08-21
--------------------------------

- First SourceForge based release.
- Added [replace functionality](http://flickrapi.sourceforge.net/flickrapi.html#flickr-replace).
- Added compatibility with graphical browsers.
- Added functionality for GUI application authentication.
- A `FlickrError` exception is now thrown when a Flickr API call returns
  an error status.
  [[ Feature request 1772031 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1772031&group_id=203043&atid=984009)
- Reorganized the package source to a Python package (it was a module).
- Instead of writing to stderr the `logging` module is now used for logging.
- No longer required to pass the API key and the authentication token
  to Flickr API calls.
  [[ Feature request 1772023 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1772023&group_id=203043&atid=984009)
- Written proper documentation
  [[ Feature request 1772026 ]](http://sourceforge.net/tracker/index.php?func=detail&aid=1772026&group_id=203043&atid=984009)


Historical versions
-------------------

Before we moved to SourceForge, there was a simple numbering
scheme from version 1 to 11. Version 11 was our first version in
Subversion, and was tagged as 0.11. From there on, a
*major.minor* numbering scheme is used. This is the
pre-Subversion changelog:

1. initial release
2. added upload functionality
3. code cleanup, convert to doc strings
4. better permission support
5. converted into fuller-featured "flickrapi"
6. fix upload sig bug (thanks Deepak Jois), encode test output
7. fix path construction, Manish Rai Jain's improvements, exceptions
8. change API endpoint to "api.flickr.com"
9. change to MIT license
10. fix horrid `\r\n` bug on final boundary
11. break out validateFrob() for subclassing
