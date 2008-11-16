'''IPTC parser for FlickrAPI'''

from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_parser.image.iptc import IPTC
from hachoir_parser.image.iptc import IPTC

def get_info(filename):
    filename = unicodeFilename(filename)
    parser = createParser(filename)
    if not parser:
        raise ValueError("Unable to parse file %s" % filename)

    return walk_tree(parser)

def handle_iptc(iptc):
    iptc_data = {
        'city': None,
        'copyright': None,
        'credit': None,
        'date_created': None,
        'keyword': [],
        'obj_name': None,
        'time_created': None,
    }

    for field in iptc:
        if field.is_field_set:
            handle_iptc(field)

        is_list = '[' in field.name and ']' in field.name

        if is_list:
            i = field.name.index('[')
            name = field.name[:i]
        else:
            name = field.name

        if name not in iptc_data:
            continue

        value = field.getField('content').value
        if is_list:
            iptc_data[name].append(value)
        else:
            iptc_data[field.name] = value

    return iptc_data

def walk_tree(parent):
    for field in parent:
        if isinstance(field, IPTC):
            return handle_iptc(field)
        if field.is_field_set:
            walk_tree(field)

#print_tree(parser)

#field = parser.getField('/photoshop/content/iptc/content/obj_name/content')
#print field.value

#index = 0
#while True:
#    path = '/photoshop/content/iptc/content/keyword[%i]/content' % index
#    try:
#        field = parser.getField(path)
#    except:
#        break
#
#    print field.value
#    index += 1

#print iptc_data
