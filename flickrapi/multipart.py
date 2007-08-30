# -*- encoding: utf-8 -*-

'''Module for encoding data as form-data/multipart'''

import uuid

class Part(object):
    '''A single part of the multipart data.
    
    >>> Part({'name': 'headline'}, 'Nice Photo')
    
    >>> image = 'photo.jpg'
    >>> Part({'name': 'photo', 'filename': image}, image.read(), 'image/jpeg')
    '''
    
    def __init__(self, parameters, payload, content_type=None):
        self.content_type = content_type
        self.parameters = parameters
        self.payload = payload

    def render(self):
        '''Renders this part -> List of Strings'''
        
        parameters = ['%s="%s"' % (k, v) for k, v in self.parameters.iteritems()]
        
        lines = ['Content-Disposition: form-data; %s' % '; '.join(parameters)]
        
        if self.content_type:
            lines.append("Content-Type: %s" % self.content_type)
        
        lines.append('')
        
        if isinstance(self.payload, unicode):
            lines.append(self.payload.encode('utf-8'))
        else:
            lines.append(self.payload)
        
        return lines

class FilePart(Part):
    '''A single part with a file as the payload
    
    This example has the same semantics as the second Part example:
    >>> FilePart({'name': 'photo'}, 'photo.jpg', 'image/jpeg')
    '''
    
    def __init__(self, parameters, filename, content_type):
        parameters['filename'] = filename
        
        imagefile = open(filename)
        payload = imagefile.read()
        imagefile.close()

        Part.__init__(self, parameters, payload, content_type)

class Multipart(object):
    '''Container for multipart data'''
    
    def __init__(self):
        '''Creates a new Multipart.'''
        
        self.parts = []
        self.content_type = 'form-data/multipart'
        self.boundary = str(uuid.uuid1()).replace('-', '.')
        
    def attach(self, part):
        '''Attaches a part'''
        
        self.parts.append(part)
    
    def __str__(self):
        '''Renders the Multipart'''

        lines = []
        for part in self.parts:
            lines += ['--' + self.boundary]
            lines += part.render()
        lines += ['--' + self.boundary + "--"]
        
        return '\r\n'.join(lines)
    
    def header(self):
        '''Returns the top-level HTTP header of this multipart'''
        
        return ("Content-Type", "multipart/form-data; boundary=%s" % self.boundary)