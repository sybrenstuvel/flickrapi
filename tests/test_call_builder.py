import unittest
import mock


class CallBuilderTest(unittest.TestCase):
    def setUp(self):
        import flickrapi
        self.f = mock.MagicMock(spec=flickrapi.FlickrAPI)

    def test_building(self):
        from flickrapi.call_builder import CallBuilder

        cb = CallBuilder(self.f)
        three = cb.one.two.three

        self.assertEqual('flickr.one.two.three', three.method_name)

    def test_calling(self):
        from flickrapi.call_builder import CallBuilder

        cb = CallBuilder(self.f)
        cb.one.two.three(a='b')

        self.f.do_flickr_call.assert_called_with('flickr.one.two.three', a='b')

    def test_name(self):
        from flickrapi.call_builder import CallBuilder

        cb = CallBuilder(self.f)
        self.assertEqual('three', cb.one.two.three.__name__)
