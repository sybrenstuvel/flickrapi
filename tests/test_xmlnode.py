# -*- encoding: utf-8 -*-

'''Unittest for the flickrapi.tokencache module'''

import unittest
import sys

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

from flickrapi.xmlnode import XMLNode

# This XML is used in the tests
xml = '''<?xml version="1.0" encoding="utf-8"?>
<rsp stat="ok">
  <photo id="2141453991">
    <owner nsid="73509078@N00" username="Sybren Stüvel" location="The Netherlands"/>
    <title>threesixtyfive | day 115</title>
    <description>An eye for an eye?</description>
    <visibility ispublic="1" isfriend="0" isfamily="0"/>
    <dates posted="1198790234" taken="2007-12-26 13:41:48" takengranularity="0" lastupdate="1198838228"/>
    <editability cancomment="0" canaddmeta="0"/>
    <usage candownload="1" canblog="0" canprint="0"/>
    <comments>3</comments>
    <notes/>
    <tags>
      <tag id="6764206-2141453991-24181" author="73509078@N00" raw="365" machine_tag="0">365</tag>
      <tag id="6764206-2141453991-1977798" author="73509078@N00" raw="365days" machine_tag="0">365days</tag>
      <tag id="6764206-2141453991-7424031" author="73509078@N00" raw="threesixtyfive" machine_tag="0">threesixtyfive</tag>
      <tag id="6764206-2141453991-731" author="73509078@N00" raw="me" machine_tag="0">me</tag>
      <tag id="6764206-2141453991-411" author="73509078@N00" raw="selfportrait" machine_tag="0">selfportrait</tag>
      <tag id="6764206-2141453991-1200512" author="73509078@N00" raw="Sybren" machine_tag="0">sybren</tag>
      <tag id="6764206-2141453991-11836799" author="73509078@N00" raw="lens:type=17-55mm F/2.8 IS USM" machine_tag="1">lens:type=1755mmf28isusm</tag>
      <tag id="6764206-2141453991-60951" author="73509078@N00" raw="merge" machine_tag="0">merge</tag>
      <tag id="6764206-2141453991-8124" author="73509078@N00" raw="twin" machine_tag="0">twin</tag>
      <tag id="6764206-2141453991-1031" author="73509078@N00" raw="tongue" machine_tag="0">tongue</tag>
      <tag id="6764206-2141453991-935" author="73509078@N00" raw="Amsterdam" machine_tag="0">amsterdam</tag>
      <tag id="6764206-2141453991-7931" author="73509078@N00" raw="gimp" machine_tag="0">gimp</tag>
      <tag id="6764206-2141453991-39180" author="73509078@N00" raw="the gimp" machine_tag="0">thegimp</tag>
    </tags>
    <urls>
      <url type="photopage">
          http://www.flickr.com/photos/sybrenstuvel/2141453991/
      </url>
    </urls>
  </photo>
</rsp>
'''

class TestXMLNode(unittest.TestCase):
    
    def setUp(self):
        self.doc = XMLNode.parse(xml, True)
        
    def testXmlStorage(self):
        '''Tests that the XML stored in the parsed document
        is equal to the XML fed to it.
        '''
        
        self.assertEqual(self.doc.xml, xml)
    
    def testParsing(self):
        '''Tests that parsing of XML works as expected.'''
        
        self.assertEqual(self.doc.photo[0]['id'], '2141453991')
        self.assertEqual(self.doc.photo[0].comments[0].text, '3')
        self.assertEqual(self.doc.photo[0].comments[0].name, u'comments')
        self.assertEqual(self.doc.photo[0].owner[0]['username'], u"Sybren Stüvel")



















