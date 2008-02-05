
'''FlickrAPI uses its own in-memory XML representation, to be able to easily
use the info returned from Flickr.

There is no need to use this module directly, you'll get XMLNode instances
from the FlickrAPI method calls.
'''

import xml.dom.minidom

__all__ = ('XMLNode', )

class XMLNode:
    """XMLNode -- generic class for holding an XML node

    xml_str = '''<xml foo="32">
    <name bar="10">Name0</name>
    <name bar="11" baz="12">Name1</name>
    </xml>'''

    f = XMLNode.parse(xml_str)

    print f.name              # xml
    print f['foo']            # 32
    print f.name              # [<name XMLNode>, <name XMLNode>]
    print f.name[0].name      # name
    print f.name[0]["bar"]    # 10
    print f.name[0].text      # Name0
    print f.name[1].name      # name
    print f.name[1]["bar"]    # 11
    print f.name[1]["baz"]    # 12

    """

    def __init__(self):
        """Construct an empty XML node."""
        self.name = ""
        self.text = ""
        self.attrib = {}
        self.xml = None

    def __setitem__(self, key, item):
        """Store a node's attribute in the attrib hash."""
        self.attrib[key] = item

    def __getitem__(self, key):
        """Retrieve a node's attribute from the attrib hash."""
        return self.attrib[key]

    @classmethod
    def __parse_element(cls, element, this_node):
        """Recursive call to process this XMLNode."""

        this_node.name = element.nodeName

        # add element attributes as attributes to this node
        for i in range(element.attributes.length):
            an = element.attributes.item(i)
            this_node[an.name] = an.nodeValue

        for a in element.childNodes:
            if a.nodeType == xml.dom.Node.ELEMENT_NODE:

                child = XMLNode()
                try:
                    getattr(this_node, a.nodeName)
                except AttributeError:
                    setattr(this_node, a.nodeName, [])

                # add the child node as an attrib to this node
                children = getattr(this_node, a.nodeName)
                children.append(child)

                cls.__parse_element(a, child)

            elif a.nodeType == xml.dom.Node.TEXT_NODE:
                this_node.text += a.nodeValue
        
        return this_node

    @classmethod
    def parse(cls, xml_str, store_xml=False):
        """Convert an XML string into a nice instance tree of XMLNodes.

        xml_str -- the XML to parse
        store_xml -- if True, stores the XML string in the root XMLNode.xml

        """

        dom = xml.dom.minidom.parseString(xml_str)

        # get the root
        root_node = XMLNode()
        if store_xml: root_node.xml = xml_str

        return cls.__parse_element(dom.firstChild, root_node)
