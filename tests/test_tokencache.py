# -*- encoding: utf-8 -*-

'''Unittest for the flickrapi.tokencache module'''

import unittest
import sys
import os.path

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi

class AbstractCacheTest(unittest.TestCase):
    '''Superclass for testing TokenCache objects.'''

    def setUp(self):
        '''Set the API key and remove the cache'''
         
        self.api_key = '123'
        self.remove_token()

    def tearDown(self):
        '''Remove the cache, again'''

        self.remove_token()

    def remove_token(self, username=None):
        tp = self.target_path(username)
        if os.path.exists(tp):
            os.unlink(tp)

    def target_path(self, username=None):
        if username:
            filename = 'auth-%s.token' % username
        else:
            filename = 'auth.token'

        return os.path.expanduser(os.path.join(
            "~", ".flickr", self.api_key, filename))

class TestCache(AbstractCacheTest):

    def test_set_get(self):
        token = 'xyz'
        
        cache = flickrapi.TokenCache(self.api_key)
        cache.token = token
        
        self.assertTrue(os.path.exists(self.target_path()))
        
        contents = open(self.target_path()).read()
        self.assertEquals(token, contents.strip())        
        self.assertEquals(token, cache.token)
    
    def test_get_from_file(self):
        token = 'xyz'

        # Store in one instance
        cache = flickrapi.TokenCache(self.api_key)
        cache.token = token
        
        # Read from another instance
        cache = flickrapi.TokenCache(self.api_key)
        self.assertEquals(token, cache.token)
    
    def test_remove(self):
        token = 'xyz'

        # Make sure the token doesn't exist yet before we start
        self.assertFalse(os.path.exists(self.target_path()))

        cache = flickrapi.TokenCache(self.api_key)

        # Make sure we can forget a token that doesn't exist
        cache.forget()
        self.assertFalse(os.path.exists(self.target_path()))
        self.assertEquals(None, cache.token)
        
        # Make sure remembering the token works
        cache.token = token
        self.assertTrue(os.path.exists(self.target_path()))
        
        # Make sure forgetting really works
        cache.forget()
        self.assertFalse(os.path.exists(self.target_path()))
        self.assertEquals(None, cache.token)

    def test_create_dir(self):
        '''Tests that the token cache can automatically create its
        storage directory.
        '''

        token_path = self.target_path()
        tokendir = os.path.dirname(token_path)
        
        # Move token dir to a temporary dir
        tempdir = None
        try:
            if os.path.exists(tokendir):
                tempdir = '%s-DO-NOT-EXIST' % tokendir
                if os.path.exists(tempdir):
                    raise Exception("Tempdir %s exists, please remove" % tempdir)
                os.rename(tokendir, tempdir)
            
            self.assertFalse(os.path.exists(tokendir))
            
            cache = flickrapi.TokenCache(self.api_key)
            cache.token = 'x'
            
            self.assertTrue(os.path.exists(tokendir))

            os.unlink(os.path.join(tokendir, 'auth.token'))
            os.rmdir(tokendir)
        finally:
            if tempdir:
                os.rename(tempdir, tokendir)

    def test_alternate_dir(self):
        '''Tests that the token cache has a configurable storage
        directory.
        '''

        cache = flickrapi.TokenCache(self.api_key)
        cache.path = '/tmp/flicktokens'
        cache.token = 'x'
        
        tokendir = os.path.join(cache.path, self.api_key)
        tokenfile = os.path.join(tokendir, 'auth.token')
        self.assertTrue(os.path.exists(tokenfile))

        # Clean up
        os.unlink(tokenfile)
        os.rmdir(tokendir)
        os.rmdir(cache.path)
        
    def test_multi_user(self):
        token = 'xyz'
        username = u'Sybren Stüvel'

        # Cache the auth token        
        cache = flickrapi.TokenCache(self.api_key, username)
        cache.token = token
        
        # Ensure the token is stored in the right place
        self.assertTrue(os.path.exists(self.target_path(username)))

        # And that it contains the proper stuff        
        contents = open(self.target_path(username)).read()
        self.assertEquals(token, contents.strip())        
        self.assertEquals(token, cache.token)
        
        # Ensure it can't be found by using another user
        cache = flickrapi.TokenCache(self.api_key, username + u'blah')
        self.assertEquals(None, cache.token)
        
        self.remove_token(username)

class TestLockingTokenCache(AbstractCacheTest):
    
    def test_set_get(self):
        token = 'xyz'
        
        cache = flickrapi.LockingTokenCache(self.api_key)
        cache.token = token

        self.assertTrue(os.path.exists(self.target_path()),
                        'Token path should exist')
        
        # Inspect the contents of the token
        contents = open(self.target_path()).read()
        self.assertEquals(token, contents.strip())        
        self.assertEquals(token, cache.token)

        # Check that the lock is gone after the operations.
        lock = cache.get_lock_name()
        self.assertFalse(os.path.exists(lock),
                         'Lock should have been removed')
