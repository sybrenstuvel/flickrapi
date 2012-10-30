
class CallBuilder(object):
    '''Builds a method name for FlickrAPI calls.

    >>> c = CallBuilder()
    >>> c.photos
    CallBuilder('flickr.photos')
    >>> c.photos.getInfo
    CallBuilder('flickr.photos.getInfo')

    '''

    def __init__(self, flickrapi_object, method_name='flickr'):
        self.flickrapi_object = flickrapi_object
        self.method_name = method_name

    def __getattr__(self, name):
        '''Returns a CallBuilder for the given name.'''

        # Refuse to act as a proxy for unimplemented special methods
        if name.startswith('_'):
            raise AttributeError("No such attribute '%s'" % name)

        return self.__class__(self.flickrapi_object,
                              self.method_name + '.' + name)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.method_name)

    def __call__(self, **kwargs):
        return self.flickrapi_object.do_flickr_call(self.method_name, **kwargs)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    c = CallBuilder('flickr')
    c.photos.getInfo(photo_id='1234')
