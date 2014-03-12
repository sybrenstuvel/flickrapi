'''Contributed FlickrAPI extensions.

These FlickrAPI extensions have been contributed by other developers. They may
not be as thoroughly tested as the core Python FlickrAPI modules.

'''

import logging
import threading

import six
http_client = six.moves.http_client

from flickrapi import core

LOG = logging.getLogger(__name__)

class PersistentFlickrAPI(core.FlickrAPI):
    '''FlickrAPI that uses persistent HTTP connections via httplib.
    
    The HTTP connection is persisted in a thread-local way.

    Note that it may be possible that the connection was closed for some
    reason, in which case a Flickr call will fail. The next call will try to
    re-establish the connection. Re-trying the call in such a case is the
    responsibility of the caller.
   
    '''

    def __init__(self, *args, **kwargs):
        core.FlickrAPI.__init__(self, *args, **kwargs)

        # Thread-local HTTPConnection, see _http_post
        self.thr = threading.local()

    def _http_post(self, post_data):
        '''Performs a HTTP POST call to the Flickr REST URL.
        
        Raises a httplib.ImproperConnectionState exception when the connection
        was closed unexpectedly.
        '''

        # Thread-local persistent connection
        try:
            if 'conn' not in self.thr.__dict__:
                self.thr.conn = http_client.HTTPConnection(self.flickr_host)
                LOG.info("connection opened to %s" % self.flickr_host, 3)

            self.thr.conn.request("POST", self.flickr_rest_form, post_data,
                    {"Content-Type": "application/x-www-form-urlencoded"})
            reply = self.thr.conn.getresponse().read()

        except http_client.ImproperConnectionState as e:
            LOG.error("connection error: %s" % e, 3)
            self.thr.conn.close()
            del self.thr.conn
            raise

        return reply

