
'''Persistent token cache management for the Flickr API'''

import os.path
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

__all__ = ('TokenCache', 'SimpleTokenCache')

class SimpleTokenCache(object):
    '''In-memory token cache.'''
    
    def __init__(self):
        self.token = None

    def forget(self):
        '''Removes the cached token'''

        self.token = None

class TokenCache(object):
    '''On-disk persistent token cache for a single application.
    
    The application is identified by the API key used. Per
    application multiple users are supported, with a single
    token per user.
    '''
    
    def __init__(self, api_key, username=None):
        '''Creates a new token cache instance'''
        
        self.api_key = api_key
        self.username = username        
        self.memory = {}
        
    def __get_cached_token_path(self):
        """Return the directory holding the app data."""
        return os.path.expanduser(os.path.join("~", ".flickr", self.api_key))

    def __get_cached_token_filename(self):
        """Return the full pathname of the cached token file."""
        
        if self.username:
            filename = 'auth-%s.token' % self.username
        else:
            filename = 'auth.token'

        return os.path.join(self.__get_cached_token_path(), filename)

    def __get_cached_token(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file.
        """

        # Only read the token once
        if self.username in self.memory:
            return self.memory[self.username]

        try:
            f = file(self.__get_cached_token_filename(), "r")
            token = f.read()
            f.close()

            return token.strip()
        except IOError:
            return None

    def __set_cached_token(self, token):
        """Cache a token for later use."""

        # Remember for later use
        self.memory[self.username] = token

        path = self.__get_cached_token_path()
        if not os.path.exists(path):
            os.makedirs(path)

        f = file(self.__get_cached_token_filename(), "w")
        print >>f, token
        f.close()

    def forget(self):
        '''Removes the cached token'''
        
        if self.username in self.memory:
            del self.memory[self.username]
        filename = self.__get_cached_token_filename()
        if os.path.exists(filename):
            os.unlink(filename)
        
    token = property(__get_cached_token, __set_cached_token, forget, "The cached token")
