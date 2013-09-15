# -*- coding: utf-8 -*-

'''Utility functions for working with network sockets.

Created by Sybren A. Stüvel for Chess IX, Haarlem, The Netherlands.
Licensed under the Apache 2 license.
'''

import socket
import os
import logging

LOG = logging.getLogger(__name__)

def is_bindable(address):
    '''Tries to bind a listening socket to the given address.
    
    Returns True if this works, False otherwise. In any case the socket is
    closed before returning.
    '''

    sock = None
    try:
        sock = socket.socket()
        if os.name == 'posix':
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(address)
        sock.close()
    except IOError as ex:
        LOG.debug('is_bindable(%s): %s', address, ex)
        if sock:
            sock.close()
        return False
    
    return True
    
def is_reachable(address):
    '''Tries to connect to the given address using a TCP socket. 
    
    Returns True iff this is possible. Always closes the connection before
    returning.
    '''
    
    try:
        sock = socket.create_connection(address, 1.0)
        sock.close()
    except IOError:
        return False
    
    return True
 
def find_free_port(start_address):
    '''Incrementally searches for a TCP port that can be bound to.
    
    :param start_address: (hostname, portnr) tuple defining the host to
                          bind and the portnumber to start the search
    :type start_address: tuple
    
    :return: the address containing the first port number that was found
             to be free.
    :rtype: tuple of (hostname, port_nr)
    '''
    
    (hostname, port_nr) = start_address

    LOG.debug('find_free_port(%s)', start_address)
    while not is_bindable((hostname, port_nr)):
        LOG.debug('find_free_port: %i is not bindable, trying next port', port_nr)        
        port_nr += 1
    
    return hostname, port_nr
