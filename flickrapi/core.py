'''The core Python FlickrAPI module.

This module contains most of the FlickrAPI code. It is well tested and
documented.
'''

from __future__ import print_function

import logging
import six
import functools

try: import cStringIO as StringIO
except ImportError: import StringIO

# Smartly import hashlib and fall back on md5
try: from hashlib import md5
except ImportError: from md5 import md5

from . import tokencache, auth

from flickrapi.xmlnode import XMLNode
from flickrapi.exceptions import *
from flickrapi.cache import SimpleCache
from flickrapi.call_builder import CallBuilder

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def make_bytes(dictionary):
    '''Encodes all Unicode strings in the dictionary to UTF-8 bytes. Converts
    all other objects to regular bytes.
    
    Returns a copy of the dictionary, doesn't touch the original.
    '''
    
    result = {}

    for (key, value) in dictionary.iteritems():
        if isinstance(value, six.text_type):
            value = value.encode('utf-8')
        else:
            value = six.binary_type(value)
        result[key] = value
    
    return result
    
def debug(method):
    '''Method decorator for debugging method calls.

    Using this automatically sets the log level to DEBUG.
    '''

    LOG.setLevel(logging.DEBUG)

    def debugged(*args, **kwargs):
        LOG.debug("Call: %s(%s, %s)" % (method.__name__, args,
            kwargs))
        result = method(*args, **kwargs)
        LOG.debug("\tResult: %s" % result)
        return result

    return debugged


# REST parsers, {format: parser_method, ...}. Fill by using the
# @rest_parser(format) function decorator
rest_parsers = {}
def rest_parser(parsed_format):
    '''Method decorator, use this to mark a function as the parser for
    REST as returned by Flickr.
    '''

    def decorate_parser(method):
        rest_parsers[parsed_format] = method
        return method

    return decorate_parser

def require_format(required_format):
    '''Method decorator, raises a ValueError when the decorated method
    is called if the default format is not set to ``required_format``.
    '''

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
    '''Method wrapper, assumed the wrapped method has a 'perms' parameter.
    
    Only calls the wrapped method if the token cache doesn't contain a valid token.
    '''
    
    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        assert isinstance(self, FlickrAPI)
        
        token = self.token_cache.token
        if 'perms' in kwargs:
            permissions = kwargs['perms']
        else:
            raise ValueError('Unable to find requested permissions, pass "perms" parameter as keyword')

        if token and token.has_level(permissions):
            self.flickr_oauth.token = token
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
    
    REST_URL = 'http://api.flickr.com/services/rest/'
    UPLOAD_URL = 'http://api.flickr.com/services/upload/'
    REPLACE_URL = 'http://api.flickr.com/services/replace/'
    
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

        self.flickr_oauth = auth.OAuthFlickrInterface(api_key, secret)

        self.default_format = format
        
        self._handler_cache = {}

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

        # TODO: what to do with cache now we use OAuth?
#        if cache:
#            self.cache = SimpleCache()
#        else:
#            self.cache = None

    def __repr__(self):
        '''Returns a string representation of this object.'''

        return '[FlickrAPI for key "%s"]' % self.flickr_oauth.key
    __str__ = __repr__

    def trait_names(self):
        '''Returns a list of method names as supported by the Flickr
        API. Used for tab completion in IPython.
        '''

        try:
            rsp = self.reflection_getMethods(format='etree')
        except FlickrError:
            return None

        return [m.text[7:] for m in rsp.getiterator('method')]

    @rest_parser('xmlnode')
    def parse_xmlnode(self, rest_xml):
        '''Parses a REST XML response from Flickr into an XMLNode object.'''

        rsp = XMLNode.parse(rest_xml, store_xml=True)
        if rsp['stat'] == 'ok':
            return rsp
        
        err = rsp.err[0]
        raise FlickrError(six.u('Error: %(code)s: %(msg)s') % err, code=err['code'])

    @rest_parser('etree')
    def parse_etree(self, rest_xml):
        '''Parses a REST XML response from Flickr into an ElementTree object.'''

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
        '''Returns a CallBuilder for the given method name.'''

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
                    'nojsoncallback': 1,
                    'format': self.default_format}
        params = self._supply_defaults(params, defaults)

        LOG.info('Calling %s', defaults)

        return self._wrap_in_parser(self._flickr_call,
                                    parse_format=params['format'],
                                    **params)

    def _supply_defaults(self, args, defaults):
        '''Returns a new dictionary containing ``args``, augmented with defaults
        from ``defaults``.

        Defaults can be overridden, or completely removed by setting the
        appropriate value in ``args`` to ``None``.

        >>> f = FlickrAPI('123')
        >>> f._supply_defaults(
        ...  {'foo': 'bar', 'baz': None, 'token': None},
        ...  {'baz': 'foobar', 'room': 'door'})
        {'foo': 'bar', 'room': 'door'}
        '''

        result = args.copy()
        for key, default_value in defaults.iteritems():
            # Set the default if the parameter wasn't passed
            if key not in args:
                result[key] = default_value

        for key, value in result.copy().iteritems():
            # You are able to remove a default by assigning None, and we can't
            # pass None to Flickr anyway.
            if value is None:
                del result[key]
        
        return result

    def _flickr_call(self, **kwargs):
        '''Performs a Flickr API call with the given arguments. The method name
        itself should be passed as the 'method' parameter.
        
        Returns the unparsed data from Flickr::

            data = self._flickr_call(method='flickr.photos.getInfo',
                photo_id='123', format='rest')
        '''

        LOG.debug("Calling %s" % kwargs)

        # Return value from cache if available
        # TODO: handle caching
#        if self.cache and self.cache.get(post_data):
#            return self.cache.get(post_data)

        reply = self.flickr_oauth.do_request(self.REST_URL, kwargs)

        # Store in cache, if we have one
        # TODO: handle caching
#        if self.cache is not None:
#            self.cache.set(post_data, reply)

        return reply

    def _wrap_in_parser(self, wrapped_method, parse_format, *args, **kwargs):
        '''Wraps a method call in a parser.

        The parser will be looked up by the ``parse_format`` specifier. If there
        is a parser and ``kwargs['format']`` is set, it's set to ``rest``, and
        the response of the method is parsed before it's returned.
        '''

        # Find the parser, and set the format to rest if we're supposed to
        # parse it.
        if parse_format in rest_parsers and 'format' in kwargs:
            kwargs['format'] = 'rest'

        LOG.debug('Wrapping call %s(self, %s, %s)' % (wrapped_method, args,
            kwargs))
        data = wrapped_method(*args, **kwargs)

        # Just return if we have no parser
        if parse_format not in rest_parsers:
            return data

        # Return the parsed data
        parser = rest_parsers[parse_format]
        return parser(self, data)

    
    def _extract_upload_response_format(self, kwargs):
        '''Returns the response format given in kwargs['format'], or
        the default format if there is no such key.

        If kwargs contains 'format', it is removed from kwargs.

        If the format isn't compatible with Flickr's upload response
        type, a FlickrError exception is raised.
        '''

        # Figure out the response format
        response_format = kwargs.get('format', self.default_format)
        if response_format not in rest_parsers and response_format != 'rest':
            raise FlickrError('Format %s not supported for uploading '
                              'photos' % response_format)

        # The format shouldn't be used in the request to Flickr.
        if 'format' in kwargs:
            del kwargs['format']

        return response_format

    def upload(self, filename, **kwargs):
        """Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        filename
            name of a file to upload
        title
            title of the photo
        description
            description a.k.a. caption of the photo
        tags
            space-delimited list of tags, ``'''tag1 tag2 "long
            tag"'''``
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

        The callback method should take two parameters:
        ``def callback(progress, done)``
        
        Progress is a number between 0 and 100, and done is a boolean
        that's true only when the upload is done.
        """

        return self._upload_to_form(self.UPLOAD_URL, filename, **kwargs)
    
    def replace(self, filename, photo_id, **kwargs):
        """Replace an existing photo.

        Supported parameters:

        filename
            name of a file to upload
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
        return self._upload_to_form(self.REPLACE_URL, filename, **kwargs)
        
    def _upload_to_form(self, form_url, filename, **kwargs):
        '''Uploads a photo - can be used to either upload a new photo
        or replace an existing one.

        form_url must be either ``FlickrAPI.flickr_replace_form`` or
        ``FlickrAPI.flickr_upload_form``.
        '''

        if not filename:
            raise IllegalArgumentException("filename must be specified")
        if not self.token_cache.token:
            raise IllegalArgumentException("Authentication is required")

        # Figure out the response format
        response_format = self._extract_upload_response_format(kwargs)

        # Convert to UTF-8 if an argument is an Unicode string
        kwargs = make_bytes(kwargs)
        
        return self._wrap_in_parser(self.flickr_oauth.do_upload, response_format,
                                    filename, form_url, kwargs)
    

    @authenticator
    def authenticate_console(self, perms='read'):
        '''Performs the authentication/authorization, assuming a console program.

        Shows the URL the user should visit on stdout, then waits for the user to authorize
        the program.
        '''

        self.flickr_oauth.get_request_token()
        authorize_url = self.flickr_oauth.auth_url(perms=perms)

        print("Go to the following link in your browser to authorize this application:")
        print(authorize_url)
        print()

        self.flickr_oauth.verifier = self.auth_http_server.wait_for_oauth_verifier()
        token = self.flickr_oauth.get_access_token()
        self.token_cache.token = token

    @authenticator
    def authenticate_via_browser(self, perms='read'):
        '''Performs the authentication/authorization, assuming a console program.

        Starts the browser and waits for the user to authorize the app before continuing.
        '''

        self.flickr_oauth.get_request_token()
        self.flickr_oauth.auth_via_browser(perms=perms)
        token = self.flickr_oauth.get_access_token()
        self.token_cache.token = token

    @require_format('etree')
    def data_walker(self, method, searchstring='*/photo', **params):
        '''Calls 'method' with page=0, page=1 etc. until the total
        number of pages has been visited. Yields the photos
        returned.
        
        Assumes that ``method(page=n, **params).findall(searchstring)``
        results in a list of interesting elements (defaulting to photos), 
        and that the toplevel element of the result contains a 'pages' 
        attribute with the total number of pages.
        '''

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
        '''walk_contacts(self, per_page=50, ...) -> \
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
        '''
        
        return self.data_walker(self.contacts_getList, searchstring='*/contact',
                                per_page=per_page, **kwargs)

    
    @require_format('etree')
    def walk_photosets(self, per_page=50, **kwargs):
        '''walk_photosets(self, per_page=50, ...) -> \
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
        '''
        
        return self.data_walker(self.photosets_getList, searchstring='*/photoset',
                                per_page=per_page, **kwargs)

    
    @require_format('etree')
    def walk_set(self, photoset_id, per_page=50, **kwargs):
        '''walk_set(self, photoset_id, per_page=50, ...) -> \
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
        '''

        return self.data_walker(self.photosets_getPhotos,
                photoset_id=photoset_id, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk_user(self, user_id='me', per_page=50, **kwargs):
        '''walk_user(self, user_id, per_page=50, ...) -> \
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
        '''

        return self.data_walker(self.people_getPhotos,
                                 user_id=user_id, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk_user_updates(self, min_date, per_page=50, **kwargs):
        '''walk_user_updates(self, user_id, per_page=50, ...) -> \
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
        '''

        return self.data_walker(self.photos_recentlyUpdated,
                min_date=min_date, per_page=per_page, **kwargs)

    @require_format('etree')
    def walk(self, per_page=50, **kwargs):
        '''walk(self, user_id=..., tags=..., ...) -> generator, \
                yields each photo in a search query result

        Accepts the same parameters as flickr.photos.search_ API call,
        except for ``page`` because all pages will be returned
        eventually.

        .. _flickr.photos.search:
            http://www.flickr.com/services/api/flickr.photos.search.html

        Also see `walk_set`.
        '''

        return self.data_walker(self.photos_search,
                per_page=per_page, **kwargs)

