
'''Persistent token cache management for the Flickr API'''

import os.path
import logging
import time
import sqlite3

from flickrapi.exceptions import LockingError, CacheDatabaseError
from flickrapi.auth import FlickrAccessToken

LOG = logging.getLogger(__name__)

__all__ = ('SimpleTokenCache', 'OAuthTokenCache')

class SimpleTokenCache(object):
    '''In-memory token cache.'''
    
    def __init__(self):
        self._token = None
    
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, token):
        self._token = token
    
    @token.deleter
    def token(self):
        self._token = None
        
    def forget(self):
        '''Removes the cached token'''

        del self.token

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
        self.path = os.path.join("~", ".flickr")

    def get_cached_token_path(self):
        """Return the directory holding the app data."""
        return os.path.expanduser(os.path.join(self.path, self.api_key))

    def get_cached_token_filename(self):
        """Return the full pathname of the cached token file."""
        
        if self.username:
            filename = 'auth-%s.token' % self.username
        else:
            filename = 'auth.token'

        return os.path.join(self.get_cached_token_path(), filename)

    def get_cached_token(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file.
        """

        # Only read the token once
        if self.username in self.memory:
            return self.memory[self.username]

        try:
            f = open(self.get_cached_token_filename(), "r")
            token = f.read()
            f.close()

            return token.strip()
        except IOError:
            return None

    def set_cached_token(self, token):
        """Cache a token for later use."""

        # Remember for later use
        self.memory[self.username] = token

        path = self.get_cached_token_path()
        if not os.path.exists(path):
            os.makedirs(path)

        f = open(self.get_cached_token_filename(), "w")
        f.write(token)
        f.close()

    def forget(self):
        '''Removes the cached token'''
        
        if self.username in self.memory:
            del self.memory[self.username]
        filename = self.get_cached_token_filename()
        if os.path.exists(filename):
            os.unlink(filename)

    token = property(get_cached_token, set_cached_token, forget, "The cached token")

class OAuthTokenCache(object):
    '''TokenCache for OAuth tokens; stores them in a SQLite database.'''

    DB_VERSION = 1
    
    # Mapping from (api_key, lookup_key) to FlickrAccessToken object.
    RAM_CACHE = {}

    def __init__(self, api_key, lookup_key=''):
        '''Creates a new token cache instance'''
        
        assert lookup_key is not None
        
        self.api_key = api_key
        self.lookup_key = lookup_key
        self.path = os.path.expanduser(os.path.join("~", ".flickr"))
        self.filename = os.path.join(self.path, 'oauth-tokens.sqlite')

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        self.create_table()

    def create_table(self):
        '''Creates the DB table, if it doesn't exist already.'''
        
        db = sqlite3.connect(self.filename)
        curs = db.cursor()
        
        # Check DB version
        curs.execute('CREATE TABLE IF NOT EXISTS oauth_cache_db_version (version int not null)')
        curs.execute('select version from oauth_cache_db_version')
        oauth_cache_db_version = curs.fetchone()
        if not oauth_cache_db_version:
            curs.execute('INSERT INTO oauth_cache_db_version (version) values (?)',
                         str(self.DB_VERSION))
        elif int(oauth_cache_db_version[0]) != self.DB_VERSION:
            raise CacheDatabaseError('Unsupported database version %s' %
                                     oauth_cache_db_version[0])
        
        # Create cache table if it doesn't exist already
        curs.execute('''CREATE TABLE IF NOT EXISTS oauth_tokens (
                        api_key varchar(64) not null,
                        lookup_key varchar(64) not null default '',
                        oauth_token varchar(64) not null,
                        oauth_token_secret varchar(64) not null,
                        access_level varchar(6) not null,
                        fullname varchar(255) not null,
                        username varchar(255) not null,
                        user_nsid varchar(64) not null,
                        PRIMARY KEY(api_key, lookup_key))''')

    @property
    def token(self):
        '''Return the cached token for this API key, or None if not found.'''

        # Only read the token once
        if (self.api_key, self.lookup_key) in self.RAM_CACHE:
            return self.RAM_CACHE[self.api_key, self.lookup_key]

        db = sqlite3.connect(self.filename)
        curs = db.cursor()
        curs.execute('''SELECT oauth_token, oauth_token_secret, access_level, fullname, username, user_nsid
                        FROM oauth_tokens WHERE api_key=? and lookup_key=?''',
                     (self.api_key, self.lookup_key))
        token_data = curs.fetchone()
        
        if token_data is None:
            return None
        
        return FlickrAccessToken(*token_data)

    @token.setter
    def token(self, token):
        """Cache a token for later use."""

        assert isinstance(token, FlickrAccessToken)

        # Remember for later use
        self.RAM_CACHE[self.api_key, self.lookup_key] = token

        db = sqlite3.connect(self.filename)
        curs = db.cursor()
        curs.execute('''INSERT OR REPLACE INTO oauth_tokens
            (api_key, lookup_key, oauth_token, oauth_token_secret, access_level, fullname, username, user_nsid)
            values (?, ?, ?, ?, ?, ?, ?, ?)''',
            (self.api_key, self.lookup_key,
             token.token, token.token_secret, token.access_level,
             token.fullname, token.username, token.user_nsid)
        )
        db.commit()

    @token.deleter
    def token(self):
        '''Removes the cached token'''

        # Delete from ram cache
        if (self.api_key, self.lookup_key) in self.RAM_CACHE:
            del self.RAM_CACHE[self.api_key, self.lookup_key]
       
        db = sqlite3.connect(self.filename)
        curs = db.cursor()
        curs.execute('''DELETE FROM oauth_tokens WHERE api_key=? and lookup_key=?''',
                     (self.api_key, self.lookup_key))
        db.commit()
        
    def forget(self):
        '''Removes the cached token'''

        del self.token

class LockingTokenCache(TokenCache):
    '''Locks the token cache when reading or updating it, so that
    multiple processes can safely use the same API key.
    '''

    def get_lock_name(self):
        '''Returns the filename of the lock.'''

        token_name = self.get_cached_token_filename()
        return '%s-lock' % token_name
    lock = property(get_lock_name)

    def get_pidfile_name(self):
        '''Returns the name of the pidfile in the lock directory.'''

        return os.path.join(self.lock, 'pid')
    pidfile_name = property(get_pidfile_name)


    def get_lock_pid(self):
        '''Returns the PID that is stored in the lock directory, or
        None if there is no such file.
        '''

        filename = self.pidfile_name
        if not os.path.exists(filename):
            return None

        pidfile = open(filename)
        try:
            pid = pidfile.read()
            if pid:
                return int(pid)
        finally:
            pidfile.close()

        return None

        
    def acquire(self, timeout=60):
        '''Locks the token cache for this key and username.

        If the token cache is already locked, waits until it is
        released. Throws an exception when the lock cannot be acquired
        after ``timeout`` seconds.
        '''

        # Check whether there is a PID file already with our PID in
        # it.
        lockpid = self.get_lock_pid()
        if lockpid == os.getpid():
            LOG.debug('The lock is ours, continuing')
            return

        # Figure out the lock filename
        lock = self.get_lock_name()
        LOG.debug('Acquiring lock %s' % lock)

        # Try to obtain the lock
        start_time = time.time()
        while True:
            try:
                os.makedirs(lock)
                break
            except OSError:
                # If the path doesn't exist, the error isn't that it
                # can't be created because someone else has got the
                # lock. Just bail out then.
                if not os.path.exists(lock):
                    LOG.error('Unable to acquire lock %s, aborting' %
                            lock)
                    raise

                if time.time() - start_time >= timeout:
                    # Timeout has passed, bail out
                    raise LockingError('Unable to acquire lock ' +
                            '%s, aborting' % lock)

                # Wait for a bit, then try again
                LOG.debug('Unable to acquire lock, waiting')
                time.sleep(0.1)

        # Write the PID file
        LOG.debug('Lock acquired, writing our PID')
        pidfile = open(self.pidfile_name, 'w')
        try:
            pidfile.write('%s' % os.getpid())
        finally:
            pidfile.close()

    def release(self):
        '''Unlocks the token cache for this key.'''

        # Figure out the lock filename
        lock = self.get_lock_name()
        if not os.path.exists(lock):
            LOG.warn('Trying to release non-existing lock %s' % lock)
            return

        # If the PID file isn't ours, abort.
        lockpid = self.get_lock_pid()
        if lockpid and lockpid != os.getpid():
            raise LockingError(('Lock %s is NOT ours, but belongs ' +
                'to PID %i, unable to release.') % (lock, lockpid))

        LOG.debug('Releasing lock %s' % lock)

        # Remove the PID file and the lock directory
        pidfile = self.pidfile_name
        if os.path.exists(pidfile):
            os.remove(pidfile)
        os.removedirs(lock)

    def __del__(self):
        '''Cleans up any existing lock.'''

        # Figure out the lock filename
        lock = self.get_lock_name()
        if not os.path.exists(lock):
            return

        # If the PID file isn't ours, we're done
        lockpid = self.get_lock_pid()
        if lockpid and lockpid != os.getpid():
            return

        # Release the lock
        self.release()

    def locked(method):
        '''Decorator, ensures the method runs in a locked cache.'''

        def locker(self, *args, **kwargs):
            self.acquire()
            try:
                return method(self, *args, **kwargs)
            finally:
                self.release()

        return locker

    @locked
    def get_cached_token(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file.
        """

        return TokenCache.get_cached_token(self)

    @locked
    def set_cached_token(self, token):
        """Cache a token for later use."""

        TokenCache.set_cached_token(self, token)

    @locked
    def forget(self):
        '''Removes the cached token'''
        
        TokenCache.forget(self)

    token = property(get_cached_token, set_cached_token, forget, "The cached token")
