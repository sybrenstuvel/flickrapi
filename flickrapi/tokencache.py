
'''Persistent token cache management for the Flickr API'''

import os.path
import logging
from xml.parsers.expat import ExpatError

from flickrapi.xmlnode import XMLNode

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

__all__ = ('TokenCache', )

class TokenCache(object):
    '''On-disk persistent token cache for a single application.
    
    The application is identified by the API key used.
    '''
    
    def __init__(self, api_key):
        '''Creates a new token cache instance'''
        
        self.api_key = api_key
        
    def __get_cached_token_path(self):
        """Return the directory holding the app data."""
        return os.path.expanduser(os.path.join("~", ".flickr", self.api_key))

    def __get_cached_token_filename(self):
        """Return the full pathname of the cached token file."""
        return os.path.join(self.__get_cached_token_path(), "auth.xml")

    def __get_cached_token(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file, which is basically the
        entire RSP response containing the auth element.
        """

        try:
            f = file(self.__get_cached_token_filename(), "r")
            
            data = f.read()
            f.close()

            rsp = XMLNode.parse(data)

            return rsp.auth[0].token[0].text
        except (ExpatError, IOError), e:
            return None

    def __set_cached_token(self, token_xml):
        """Cache a token for later use.

        The cached tag is stored by simply saving the entire RSP response
        containing the auth element.

        """

        path = self.__get_cached_token_path()
        if not os.path.exists(path):
            os.makedirs(path)

        f = file(self.__get_cached_token_filename(), "w")
        f.write(token_xml)
        f.close()

    def forget(self):
        '''Removes the cached token'''
        
        os.unlink(self.__get_cached_token_filename())
        
    token = property(__get_cached_token, __set_cached_token, forget, "The cached token")