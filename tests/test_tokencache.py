# -*- encoding: utf-8 -*-

'''Unittest for the flickrapi.tokencache module'''

import unittest
import sys
import os.path

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi

class TestCache(unittest.TestCase):

    def setUp(self):
        '''Set the API key and remove the cache'''
         
        self.api_key = '123'
        self.remove_token()

    def tearDown(self):
        '''Remove the cache, again'''

        self.remove_token()

    def remove_token(self):
        tp = self.target_path()
        if os.path.exists(tp):
            os.unlink(tp)

    def target_path(self):
        return os.path.expanduser(os.path.join(
            "~", ".flickr", self.api_key, 'auth.xml'))
    
    def test_set_get(self):
        token = 'xyz'
        xml = '''<rsp stat='ok'><auth><token>%s</token></auth></rsp>''' % token
        
        cache = flickrapi.TokenCache(self.api_key)
        cache.token = xml
        
        self.assertTrue(os.path.exists(self.target_path()))
        
        contents = file(self.target_path()).read()
        self.assertEquals(xml, contents)        
        self.assertEquals(token, cache.token)
    
    def test_remove(self):
        token = 'xyz'
        xml = '''<rsp stat='ok'><auth><token>%s</token></auth></rsp>''' % token
        
        cache = flickrapi.TokenCache(self.api_key)
        cache.token = xml
        
        self.assertTrue(os.path.exists(self.target_path()))
        
        cache.forget()
        
        self.assertFalse(os.path.exists(self.target_path()))
        self.assertEquals(None, cache.token)
        
    def test_get_invalid_xml(self):
        token_path = self.target_path()
        tokendir = os.path.dirname(token_path)
        if not os.path.exists(tokendir):
            os.makedirs(tokendir)
        
        tokenfile = file(token_path, 'w')
        tokenfile.write('ABC')
        
        cache = flickrapi.TokenCache(self.api_key)
        
        self.assertEquals(None, cache.token)
    
    def test_create_dir(self):
        token_path = self.target_path()
        tokendir = os.path.dirname(token_path)
        
        # Move token dir to a temporary dir
        tempdir = None
        if os.path.exists(tokendir):
            tempdir = '%s-DO-NOT-EXIST' % tokendir
            if os.path.exists(tempdir):
                raise Exception("Tempdir %s exists, please remove" % tempdir)
            os.rename(tokendir, tempdir)
        
        self.assertFalse(os.path.exists(tokendir))
        
        cache = flickrapi.TokenCache(self.api_key)
        cache.token = '''<rsp stat='ok'><auth><token>x</token></auth></rsp>'''
        
        self.assertTrue(os.path.exists(tokendir))

        os.unlink(os.path.join(tokendir, 'auth.xml'))
        os.rmdir(tokendir)
        
        if tempdir:
            os.rename(tempdir, tokendir)
