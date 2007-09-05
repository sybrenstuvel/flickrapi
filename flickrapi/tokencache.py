
'''Persistent token cache management for the Flickr API'''

import os.path

from flickrapi.xmlnode import XMLNode

__all__ = ('TokenCache', )

class TokenCache(object):
    '''On-disk persistent token cache for a single application.
    
    The application is identified by the API key used.
    '''
    
    def __init__(self, api_key):
        '''Creates a new token cache instance'''
        
        self.api_key = api_key
        
    def __getCachedTokenPath(self):
        """Return the directory holding the app data."""
        return os.path.expanduser(os.path.join("~", ".flickr", self.api_key))

    def __getCachedTokenFilename(self):
        """Return the full pathname of the cached token file."""
        return os.path.join(self.__getCachedTokenPath(), "auth.xml")

    def __getCachedToken(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file, which is basically the
        entire RSP response containing the auth element.
        """

        try:
            f = file(self.__getCachedTokenFilename(), "r")
            
            data = f.read()
            f.close()

            rsp = XMLNode.parseXML(data)

            return rsp.auth[0].token[0].elementText

        except Exception:
            return None

    def __setCachedToken(self, token_xml):
        """Cache a token for later use.

        The cached tag is stored by simply saving the entire RSP response
        containing the auth element.

        """

        path = self.__getCachedTokenPath()
        if not os.path.exists(path):
            os.makedirs(path)

        f = file(self.__getCachedTokenFilename(), "w")
        f.write(token_xml)
        f.close()

    def forget(self):
        '''Removes the cached token'''
        
        os.unlink(self.__getCachedTokenFilename())
        
    token = property(__getCachedToken, __setCachedToken, forget, "The cached token")