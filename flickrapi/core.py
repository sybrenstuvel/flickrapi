"""The core Python FlickrAPI module.

This module contains most of the FlickrAPI code. It is well tested and
documented.
"""

from __future__ import print_function

import logging
import six
import functools

from . import tokencache, auth

from flickrapi.xmlnode import XMLNode
from flickrapi.exceptions import *
from flickrapi.cache import SimpleCache
from flickrapi.call_builder import CallBuilder

LOG = logging.getLogger(__name__)


def make_bytes(dictionary):
    """Encodes all Unicode strings in the dictionary to UTF-8 bytes. Converts
    all other objects to regular bytes.
    
    Returns a copy of the dictionary, doesn't touch the original.
    """
    
    result = {}

    for (key, value) in six.iteritems(dictionary):
        # Keep binary data as-is.
        if isinstance(value, six.binary_type):
            result[key] = value
            continue

        # If it's not a string, convert it to one.
        if not isinstance(value, six.text_type):
            value = six.text_type(value)

        result[key] = value.encode('utf-8')
    
    return result
    
def debug(method):
    """Method decorator for debugging method calls.

    Using this automatically sets the log level to DEBUG.
    """

    def debugged(*args, **kwargs):
        LOG.debug("Call: %s(%s, %s)" % (method.__name__, args,
            kwargs))
        result = method(*args, **kwargs)
        LOG.debug("\tResult: %s" % result)
        return result

    return debugged


# REST parsers, {format: (parser_method, request format), ...}. Fill by using the
# @rest_parser(format) function decorator
rest_parsers = {}
def rest_parser(parsed_format, request_format='rest'):
    """Method decorator, use this to mark a function as the parser for
    REST as returned by Flickr.
    """

    def decorate_parser(method):
        rest_parsers[parsed_format] = (method, request_format)
        return method

    return decorate_parser

def require_format(required_format):
    """Method decorator, raises a ValueError when the decorated method
    is called if the default format is not set to ``required_format``.
    """

    def decorator(method):
        @functools.wraps(method)
        def decorated(self, *args, **kwargs):
            # If everything is okay, call the method
            if self.default_format == required_format:
                return method(self, *args, **kwargs)

            # Otherwise raise an exception
            msg = 'Function %s requires that you use ' \
                  'ElementTree ("etree") as the communication format, ' \
                  'while the current format is set to "%s".'
            raise ValueError(msg % (method.func_name, self.default_format))

        return decorated
    return decorator

def authenticator(method):
    """Method wrapper, assumed the wrapped method has a 'perms' parameter.
    
    Only calls the wrapped method if the token cache doesn't contain a valid token.
    """
    
    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        assert isinstance(self, FlickrAPI)
        
        if 'perms' in kwargs:
            perms = kwargs['perms']
        elif len(args):
            perms = args[0]
        else:
            perms = 'read'
        
        if self.token_valid(perms=perms):
            # Token is valid, and for the expected permissions, so no
            # need to continue authentication.
            return
        
        method(self, *args, **kwargs)
    
    return decorated
    
    

class FlickrAPI(object):
    """Encapsulates Flickr functionality.
    
    Example usage::
      
      flickr = flickrapi.FlickrAPI(api_key)
      photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
      sets = flickr.photosets_getList(user_id='73509078@N00')
    """
    
    REST_URL = 'https://api.flickr.com/services/rest/'
    UPLOAD_URL = 'https://up.flickr.com/services/upload/'
    REPLACE_URL = 'https://up.flickr.com/services/replace/'
    
    def __init__(self, api_key, secret, username=None,
            token=None, format='etree', store_token=True,
            cache=False):
        """Construct a new FlickrAPI instance for a given API key
        and secret.
        
        api_key
            The API key as obtained from Flickr.
        
        secret
            The secret belonging to the API key.
        
        username
            Used to identify the appropriate authentication token for a
            certain user.
        
        token
            If you already have an authentication token, you can give
            it here. It won't be stored on disk by the FlickrAPI instance.

        format
            The response format. Use either "xmlnode" or "etree" to get a parsed
            response, or use any response format supported by Flickr to get an
            unparsed response from method calls. It's also possible to pass the
            ``format`` parameter on individual calls.

        store_token
            Disables the on-disk token cache if set to False (default is True).
            Use this to ensure that tokens aren't read nor written to disk, for
            example in web applications that store tokens in cookies.

        cache
            Enables in-memory caching of FlickrAPI calls - set to ``True`` to
            use. If you don't want to use the default settings, you can
            instantiate a cache yourself too:

            >>> f = FlickrAPI(u'123', u'123')
            >>> f.cache = SimpleCache(timeout=5, max_entries=100)
        """


        self.default_format = format
        self._handler_cache = {}

        if isinstance(api_key, six.binary_type):
            api_key = api_key.decode('ascii')
        if isinstance(secret, six.binary_type):
            secret = secret.decode('ascii')

        if token:
            assert isinstance(token, auth.FlickrAccessToken)

            # Use a memory-only token cache
            self.token_cache = tokencache.SimpleTokenCache()
            self.token_cache.token = token
        elif not store_token:
            # Use an empty memory-only token cache
            self.token_cache = tokencache.SimpleTokenCache()
        else:
            # Use a real token cache
            self.token_cache = tokencache.OAuthTokenCache(api_key, username or '')

        self.flickr_oauth = auth.OAuthFlickrInterface(api_key, secret, self.token_cache)

        if cache:
            self.cache = SimpleCache()
        else:
            self.cache = None

    def __repr__(self):
        """Returns a string representation of this object."""

        return '[FlickrAPI for key "%s"]' % self.flickr_oauth.key
    __str__ = __repr__

    def trait_names(self):
        """Returns a list of method names as supported by the Flickr
        API. Used for tab completion in IPython.
        """

        try:
            rsp = self.reflection_getMethods(format='etree')
        except FlickrError:
            return None

        return [m.text[7:] for m in rsp.getiterator('method')]

    @rest_parser('xmlnode')
    def parse_xmlnode(self, rest_xml):
        """Parses a REST XML response from Flickr into an XMLNode object."""

        rsp = XMLNode.parse(rest_xml, store_xml=True)
        if rsp['stat'] == 'ok':
            return rsp
        
        err = rsp.err[0]
        raise FlickrError(six.u('Error: %(code)s: %(msg)s') % err, code=err['code'])

    @rest_parser('parsed-json', 'json')
    def parse_json(self, json_string):
        """Parses a JSON response from Flickr."""

        if isinstance(json_string, six.binary_type):
            json_string = json_string.decode('utf-8')

        import json
        parsed = json.loads(json_string)
        if parsed.get('stat', '') == 'fail':
            raise FlickrError(six.u('Error: %(code)s: %(message)s') % parsed,
                              code=parsed['code'])
        return parsed

    @rest_parser('etree')
    def parse_etree(self, rest_xml):
        """Parses a REST XML response from Flickr into an ElementTree object."""

        try:
            from lxml import etree as ElementTree
            LOG.info('REST Parser: using lxml.etree')
        except ImportError:
            try:
                import xml.etree.cElementTree as ElementTree
                LOG.info('REST Parser: using xml.etree.cElementTree')
            except ImportError:
                try:
                    import xml.etree.ElementTree as ElementTree
                    LOG.info('REST Parser: using xml.etree.ElementTree')
                except ImportError:
                    try:
                        import elementtree.cElementTree as ElementTree
                        LOG.info('REST Parser: elementtree.cElementTree')
                    except ImportError:
                        try:
                            import elementtree.ElementTree as ElementTree
                        except ImportError:
                            raise ImportError("You need to install "
                                "ElementTree to use the etree format")

        rsp = ElementTree.fromstring(rest_xml)
        if rsp.attrib['stat'] == 'ok':
            return rsp
        
        err = rsp.find('err')
        code = err.attrib.get('code', None)
        raise FlickrError(six.u('Error: %(code)s: %(msg)s') % err.attrib, code=code)

    def __getattr__(self, method_name):
        """Returns a CallBuilder for the given method name."""

        # Refuse to do anything with special methods
        if method_name.startswith('_'):
            raise AttributeError(method_name)
        
        # Compatibility with old way of calling, i.e. flickrobj.photos_getInfo(...)
        if '_' in method_name:
            method_name = method_name.replace('_', '.')

        return CallBuilder(self, method_name='flickr.' + method_name)

    def do_flickr_call(self, method_name, **kwargs):
        """Handle all the regular Flickr API calls.
        
        Example::

            etree = flickr.photos.getInfo(photo_id='1234')
            etree = flickr.photos.getInfo(photo_id='1234', format='etree')
            xmlnode = flickr.photos.getInfo(photo_id='1234', format='xmlnode')
            json = flickr.photos.getInfo(photo_id='1234', format='json')
        """

        params = kwargs.copy()

        # Set some defaults
        defaults = {'method': method_name,
                    'format': self.default_format}
        if 'jsoncallback' not in kwargs:
            defaults['nojsoncallback'] = 1
        params = self._supply_defaults(params, defaults)

        LOG.info('Calling %s', defaults)

        return self._wrap_in_parser(self._flickr_call,
                                    parse_format=params['format'],
                                    **params)

    def _supply_defaults(self, args, defaults):
        """Returns a new dictionary containing ``args``, augmented with defaults
        from ``defaults``.

        Defaults can be overridden, or completely removed by setting the
        appropriate value in ``args`` to ``None``.
        """

        result = args.copy()
        for key, default_value in six.iteritems(defaults):
            # Set the default if the parameter wasn't passed
            if key not in args:
                result[key] = default_value

        for key, value in six.iteritems(result.copy()):
            # You are able to remove a default by assigning None, and we can't
            # pass None to Flickr anyway.
            if value is None:
                del result[key]
        
        return result

    def _flickr_call(self, **kwargs):
        """Performs a Flickr API call with the given arguments. The method name
        itself should be passed as the 'method' parameter.
        
        Returns the unparsed data from Flickr::

            data = self._flickr_call(method='flickr.photos.getInfo',
                photo_id='123', format='rest')
        """

        LOG.debug("Calling %s" % kwargs)

        # Return value from cache if available
        if self.cache and self.cache.get(kwargs):
            return self.cache.get(kwargs)

        reply = self.flickr_oauth.do_request(self.REST_URL, kwargs)

        # Store in cache, if we have one
        if self.cache is not None:
            self.cache.set(kwargs, reply)

        return reply

    def _wrap_in_parser(self, wrapped_method, parse_format, *args, **kwargs):
        """Wraps a method call in a parser.

        The parser will be looked up by the ``parse_format`` specifier. If there
        is a parser and ``kwargs['format']`` is set, it's set to ``rest``, and
        the response of the method is parsed before it's returned.
        """

        # Find the parser, and set the format to rest if we're supposed to
        # parse it.
        if parse_format in rest_parsers and 'format' in kwargs:
            kwargs['format'] = rest_parsers[parse_format][1]

        LOG.debug('Wrapping call %s(self, %s, %s)' % (wrapped_method, args, kwargs))
        data = wrapped_method(*args, **kwargs)

        # Just return if we have no parser
        if parse_format not in rest_parsers:
            return data

        # Return the parsed data
        parser = rest_parsers[parse_format][0]
        return parser(self, data)

    
    def _extract_upload_response_format(self, kwargs):
        """Returns the response format given in kwargs['format'], or
        the default format if there is no such key.

        If kwargs contains 'format', it is removed from kwargs.

        If the format isn't compatible with Flickr's upload response
        type, a FlickrError exception is raised.
        """

        # Figure out the response format
        response_format = kwargs.get('format', self.default_format)
        if response_format not in rest_parsers and response_format != 'rest':
            raise FlickrError('Format %s not supported for uploading '
                              'photos' % response_format)

        # The format shouldn't be used in the request to Flickr.
        if 'format' in kwargs:
            del kwargs['format']

        return response_format

    def upload(self, filename, fileobj=None, **kwargs):
        """Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        filename
            name of a file to upload
        fileobj
            an optional file-like object from which the data can be read
        title
            title of the photo
        description
            description a.k.a. caption of the photo
        tags
            space-delimited list of tags, ``'''tag1 tag2 "long tag"'''``
        is_public
            "1" or "0" for a public resp. private photo
        is_friend
            "1" or "0" whether friends can see the photo while it's
            marked as private
        is_family
            "1" or "0" whether family can see the photo while it's
            marked as private
        content_type
            Set to "1" for Photo, "2" for Screenshot, or "3" for Other.
        hidden
            Set to "1" to keep the photo in global search results, "2"
            to hide from public searches.
        format
            The response format. You can only choose between the
            parsed responses or 'rest' for plain REST.

        The ``fileobj`` parameter can be used to monitor progress via
        a callback method. For example::

            class FileWithCallback(object):
                def __init__(self, filename, callback):
                    self.file = open(filename, 'rb')
                    self.callback = callback
                    # the following attributes and methods are required
                    self.len = os.path.getsize(path)
                    self.fileno = self.file.fileno
                    self.tell = self.file.tell

                def read(self, size):
                    if self.callback:
                        self.callback(self.tell() * 100 // self.len)
                    return self.file.read(size)

            fileobj = FileWithCallback(filename, callback)
            rsp = flickr.upload(filename, fileobj, parameters)

        The callback method takes one parameter:
        ``def callback(progress)``
        
        Progress is a number between 0 and 100.
        """

        return self._upload_to_form(self.UPLOAD_URL, filename, fileobj, **kwargs)
    
    def replace(self, filename, photo_id, fileobj=None, **kwargs):
        """Replace an existing photo.

        Supported parameters:

        filename
            name of a file to upload
        fileobj
            an optional file-like object from which the data can be read
        photo_id
            the ID of the photo to replace
        format
            The response format. You can only choose between the
            parsed responses or 'rest' for plain REST. Defaults to the
            format passed to the constructor.

        """
        
        if not photo_id:
            raise IllegalArgumentException("photo_id must be specified")

        kwargs['photo_id'] = photo_id
        return self._upload_to_form(self.REPLACE_URL, filename, fileobj, **kwargs)
        
    def _upload_to_form(self, form_url, filename, fileobj=None, **kwargs):
        """Uploads a photo - can be used to either upload a new photo
        or replace an existing one.

        form_url must be either ``FlickrAPI.flickr_replace_form`` or
        ``FlickrAPI.flickr_upload_form``.
        """

        if not filename:
            raise IllegalArgumentException("filename must be specified")
        if not self.token_cache.token:
            raise IllegalArgumentException("Authentication is required")

        kwargs['api_key'] = self.flickr_oauth.key

        # Figure out the response format
        response_format = self._extract_upload_response_format(kwargs)

        # Convert to UTF-8 if an argument is an Unicode string
        kwargs = make_bytes(kwargs)
        
        return self._wrap_in_parser(self.flickr_oauth.do_upload, response_format,
                                    filename, form_url, kwargs, fileobj)
    
    def token_valid(self, perms='read'):
        """Verifies the cached token with Flickr.
        
        If the token turns out to be invalid, or with permissions lower than required,
        the token is erased from the token cache.
        
        @return: True if the token is valid for the requested parameters, False otherwise.
        """
        
        token = self.token_cache.token
        
        if not token:
            return False
    
        # Check token for validity
        self.flickr_oauth.token = token
        
        try:
            resp = self.auth.oauth.checkToken(format='etree')
            token_perms = resp.findtext('oauth/perms')
            if token_perms == token.access_level and token.has_level(perms):
                # Token is valid, and for the expected permissions.
                return True

        except FlickrError:
            # There was an error talking to Flickr, we assume this is due
            # to an invalid token.
            pass
        
        # Token was for other permissions, so erase it as it is
        # not usable for this request.
        self.flickr_oauth.token = None
        del self.token_cache.token

        return False
    
    @authenticator
    def authenticate_console(self, perms='read'):
        """Performs the authentication/authorization, assuming a console program.

        Shows the URL the user should visit on stdout, then waits for the user to authorize
        the program.
        """

        if isinstance(perms, six.binary_type):
            perms = six.u(perms)

        self.flickr_oauth.get_request_token()
        self.flickr_oauth.auth_via_console(perms=perms)
        token = self.flickr_oauth.get_access_token()
        self.token_cache.token = token

    @authenticator
    def authenticate_via_browser(self, perms='read'):
        """Performs the authentication/authorization, assuming a console program.

        Starts the browser and waits for the user to authorize the app before continuing.
        """

        if isinstance(perms, six.binary_type):
            perms = six.u(perms)

        self.flickr_oauth.get_request_token()
        self.flickr_oauth.auth_via_browser(perms=perms)
        token = self.flickr_oauth.get_access_token()
        self.token_cache.token = token

    def get_request_token(self, oauth_callback=None):
        """Requests a new request token.
        
        Updates this OAuthFlickrInterface object to use the request token on the following
        authentication calls.
        
        @param oauth_callback: the URL the user is sent to after granting the token access.
            If the callback is None, a local web server is started on a random port, and the
            callback will be http://localhost:randomport/
            
            If you do not have a web-app and you also do not want to start a local web server,
            pass oauth_callback='oob' and have your application accept the verifier from the
            user instead. 
        """

        self.flickr_oauth.get_request_token(oauth_callback=oauth_callback)

    def auth_url(self, perms='read'):
        """Returns the URL the user should visit to authenticate the given oauth Token.
        
        Use this method in webapps, where you can redirect the user to the returned URL.
        After authorization by the user, the browser is redirected to the callback URL,
        which will contain the OAuth verifier. Set the 'verifier' property on this object
        in order to use it.
        
        In stand-alone apps, authenticate_via_browser(...) may be easier instead.
        """
        
        return self.flickr_oauth.auth_url(perms=perms)

    def get_access_token(self, verifier=None):
        """Exchanges the request token for an access token.

        Also stores the access token for easy authentication of subsequent calls.
        
        @param verifier: the verifier code, in case you used out-of-band communication
            of the verifier code.
        """

        if verifier is not None:
            self.flickr_oauth.verifier = verifier

        self.token_cache.token = self.flickr_oauth.get_access_token()

    @require_format('etree')
    def data_walker(self, method, searchstring='*/photo', **params):
        """Calls 'method' with page=0, page=1 etc. until the total
        number of pages has been visited. Yields the photos
        returned.
        
        Assumes that ``method(page=n, **params).findall(searchstring)``
        results in a list of interesting elements (defaulting to photos), 
        and that the toplevel element of the result contains a 'pages' 
        attribute with the total number of pages.
        """

        page = 1
        total = 1 # We don't know that yet, update when needed
        while page <= total:
            # Fetch a single page of photos
            LOG.debug('Calling %s(page=%i of %i, %s)' %
                    (method.func_name, page, total, params))
            rsp = method(page=page, **params)

            photoset = rsp.getchildren()[0]
            total = int(photoset.get('pages'))

            photos = rsp.findall(searchstring)

            # Yield each photo
            for photo in photos:
                yield photo

            # Ready to get the next page
            page += 1

    @require_format('etree')
    def walk_contacts(self, per_page=50, **kwargs):
        """walk_contacts(self, per_page=50, ...) -> \
                generator, yields each contact of the calling user.
    
        :Parameters:
            per_page
                the number of contacts that are fetched in one call to
                Flickr.
    
        Other arguments can be passed, as documented in the
        flickr.contacts.getList_ API call in the Flickr API
        documentation, except for ``page`` because all pages will be
        returned eventually.
    
        .. _flickr.contacts.getList:
            http://www.flickr.com/services/api/flickr.contacts.getList.html
    
        Uses the ElementTree format, incompatible with other formats.
        """
        
        return self.data_walker(self.contacts_getList, searchstring='*/contact',
                                per_page=per_page, **kwargs)

    
    @require_format('etree')
    def walk_photosets(self, per_page=50, **kwargs):
        """walk_photosets(self, per_page=50, ...) -> \
                generator, yields each photoset belonging to a user.
    
        :Parameters:
            per_page
                the number of photosets that are fetched in one call to
                Flickr.
    
        Other arguments can be passed, as documented in the
        flickr.photosets.getList_ API call in the Flickr API
        documentation, except for ``page`` because all pages will be
        returned eventually.
    
        .. _flickr.photosets.getList:
            http://www.flickr.com/services/api/flickr.photosets.getList.html
    
        Uses the ElementTree format, incompatible with other formats.
        """
        
        return self.data_walker(self.photosets_getList, searchstring='*/photoset',
                                per_page=per_page, **kwargs)

    
    @require_format('etree')
    def walk_set(self, photoset_id, per_page=50, **kwargs):
        """walk_set(self, photoset_id, per_page=50, ...) -> \
                generator, yields each photo in a single set.

        :Parameters:
            photoset_id
                the photoset ID
            per_page
                the number of photos that are fetched in one call to
                Flickr.

        Other arguments can be passed, as documented in the
        flickr.photosets.getPhotos_ API call in the Flickr API
        documentation, except for ``page`` because all pages will be
        returned eventually.

        .. _flickr.photosets.getPhotos:
            http://www.flickr.com/services/api/flickr.photosets.getPhotos.html
        
        Uses the ElementTree format, incompatible with other formats.
        """

        return self.data_walker(self.photosets_getPhotos,
                photoset_id=photoset_id, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk_user(self, user_id='me', per_page=50, **kwargs):
        """walk_user(self, user_id, per_page=50, ...) -> \
                generator, yields each photo in a user's photostream.

        :Parameters:
            user_id
                the user ID, or 'me'
            per_page
                the number of photos that are fetched in one call to
                Flickr.

        Other arguments can be passed, as documented in the
        flickr.people.getPhotos_ API call in the Flickr API
        documentation, except for ``page`` because all pages will be
        returned eventually.

        .. _flickr.people.getPhotos:
            http://www.flickr.com/services/api/flickr.people.getPhotos.html
        
        Uses the ElementTree format, incompatible with other formats.
        """

        return self.data_walker(self.people_getPhotos,
                                 user_id=user_id, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk_user_updates(self, min_date, per_page=50, **kwargs):
        """walk_user_updates(self, user_id, per_page=50, ...) -> \
                generator, yields each photo in a user's photostream updated \
                after ``min_date``

        :Parameters:
            min_date
                
            per_page
                the number of photos that are fetched in one call to
                Flickr.

        Other arguments can be passed, as documented in the
        flickr.photos.recentlyUpdated API call in the Flickr API
        documentation, except for ``page`` because all pages will be
        returned eventually.

        .. _flickr.photos.recentlyUpdated:
            http://www.flickr.com/services/api/flickr.photos.recentlyUpdated.html
        
        Uses the ElementTree format, incompatible with other formats.
        """

        return self.data_walker(self.photos_recentlyUpdated,
                min_date=min_date, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk(self, per_page=50, **kwargs):
        """walk(self, user_id=..., tags=..., ...) -> generator, \
                yields each photo in a search query result

        Accepts the same parameters as flickr.photos.search_ API call,
        except for ``page`` because all pages will be returned
        eventually.

        .. _flickr.photos.search:
            http://www.flickr.com/services/api/flickr.photos.search.html

        Also see `walk_set`.
        """

        return self.data_walker(self.photos.search,
                per_page=per_page, **kwargs)

