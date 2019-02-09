# -*- encoding: utf-8 -*-
import unittest


class SimpleTokenCacheTest(unittest.TestCase):
    def setUp(self):
        from flickrapi.tokencache import SimpleTokenCache
        self.tc = SimpleTokenCache()

    def test_get_set_del(self):
        self.assertIsNone(self.tc.token)

        self.tc.token = 'nümbér'
        self.assertEqual(self.tc.token, 'nümbér')

        del self.tc.token
        self.assertIsNone(self.tc.token)

        self.tc.token = 'nümbér'
        self.tc.forget()
        self.assertIsNone(self.tc.token)


class TokenCacheTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        from flickrapi.tokencache import TokenCache

        # Use mkdtemp() for backward compatibility with Python 2.7
        self.tc_path = tempfile.mkdtemp()
        self.tc = TokenCache('123-456', path=self.tc_path)

    def tearDown(self):
        tc_path = getattr(self, 'tc_path', None)
        if tc_path is not None:
            import shutil
            shutil.rmtree(self.tc_path)

    def test_get_set_del(self):
        self.assertIsNone(self.tc.token)

        # Check setting token, both in memory and on disk.
        self.tc.token = u'nümbér'
        self.assertEqual(self.tc.token, u'nümbér')
        on_disk = open(self.tc.get_cached_token_filename(), 'rb').read()
        self.assertEqual(on_disk.decode('utf8'), u'nümbér')

        # Erase from in-RAM cache and try again, to read from disk.
        self.tc.memory.clear()
        self.assertEqual(self.tc.token, u'nümbér')

        del self.tc.token
        self.assertIsNone(self.tc.token)

        self.tc.token = u'nümbér'
        self.tc.forget()
        self.assertIsNone(self.tc.token)

    def test_username(self):
        """Username should impact the location of the cache on disk."""

        from flickrapi.tokencache import TokenCache

        user_tc = TokenCache(u'123-456', username=u'frøbel', path=self.tc_path)

        tc_path = self.tc.get_cached_token_filename()
        user_path = user_tc.get_cached_token_filename()

        self.assertNotEquals(tc_path, user_path)
        self.assertNotIn(u'frøbel', tc_path)
        self.assertIn(u'frøbel', user_path)


class OAuthTokenCache(unittest.TestCase):
    def setUp(self):
        import tempfile
        from flickrapi.tokencache import OAuthTokenCache
        from flickrapi.auth import FlickrAccessToken

        # Use mkdtemp() for backward compatibility with Python 2.7
        self.tc_path = tempfile.mkdtemp()
        self.tc = OAuthTokenCache('123-456', path=self.tc_path)
        self.token = FlickrAccessToken(
            u'nümbér', u'səcret-tøken', u'read',
            u'My Full Name™', u'üsernåme', u'user—nsid',
        )

    def tearDown(self):
        tc_path = getattr(self, 'tc_path', None)
        if tc_path is not None:
            import shutil
            shutil.rmtree(self.tc_path)

    def test_get_set_del(self):
        self.assertIsNone(self.tc.token)

        # Check setting token
        self.tc.token = self.token
        self.assertEqual(self.tc.token.token, u'nümbér')

        # Erase from in-RAM cache and try again, to read from disk.
        self.tc.RAM_CACHE.clear()
        self.assertEqual(self.tc.token.token, u'nümbér')
        self.assertEqual(self.tc.token.token_secret, u'səcret-tøken')
        self.assertEqual(self.tc.token.access_level, u'read')
        self.assertEqual(self.tc.token.fullname, u'My Full Name™')
        self.assertEqual(self.tc.token.username, u'üsernåme')
        self.assertEqual(self.tc.token.user_nsid, u'user—nsid')

        del self.tc.token
        self.assertIsNone(self.tc.token)

        self.tc.token = self.token
        self.tc.forget()
        self.assertIsNone(self.tc.token)
