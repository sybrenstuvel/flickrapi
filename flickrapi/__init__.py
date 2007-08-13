#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A FlickrAPI interface.

See http://flickrapi.sf.net/ for more info.
'''

__version__ = '0.12-beta1'
__revision__ = '$Revision$'
__all__ = ('FlickrAPI', 'IllegalArgumentException', 'XMLNode', '__version__', '__revision__')

# Copyright (c) 2007 by the respective coders, see
# http://flickrapi.sf.net/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import md5
import urllib
import urllib2
import mimetools
import os.path
import logging

from flickrapi.tokencache import TokenCache
from flickrapi.xmlnode import XMLNode

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

########################################################################
# Exceptions
########################################################################

class IllegalArgumentException(ValueError):
    '''Raised when a method is passed an illegal argument.
    
    More specific details will be included in the exception message
    when thrown.
    '''


########################################################################
# Flickr functionality
########################################################################

#-----------------------------------------------------------------------
class FlickrAPI:
    """Encapsulated flickr functionality.

    Example usage:

      flickr = FlickrAPI(flickrAPIKey, flickrSecret)
      rsp = flickr.auth_checkToken(api_key=flickrAPIKey, auth_token=token)

    """
    
    flickrHost = "api.flickr.com"
    flickrRESTForm = "/services/rest/"
    flickrAuthForm = "/services/auth/"
    flickrUploadForm = "/services/upload/"
    flickrReplaceForm = "/services/replace/"

    #-------------------------------------------------------------------
    def __init__(self, apiKey, secret):
        """Construct a new FlickrAPI instance for a given API key and secret."""
        self.apiKey = apiKey
        self.secret = secret
        self.token_cache = TokenCache(apiKey)
        
        self.__handlerCache={}

    def __repr__(self):
        return '[FlickrAPI for key "%s"]' % self.apiKey
    __str__ = __repr__
    
    #-------------------------------------------------------------------
    def __sign(self, data):
        """Calculate the flickr signature for a set of params.

        data -- a hash of all the params and values to be hashed, e.g.
                {"api_key":"AAAA", "auth_token":"TTTT"}

        """
        dataName = self.secret
        keys = data.keys()
        keys.sort()
        for a in keys: dataName += (a + str(data[a]))
        #print dataName
        
        md5_hash = md5.new()
        md5_hash.update(dataName)
        return md5_hash.hexdigest()

    #-------------------------------------------------------------------
    def __getattr__(self, method):
        """Handle all the flickr API calls.
        
        This is Michele Campeotto's cleverness, wherein he writes a
        general handler for methods not defined, and assumes they are
        flickr methods.  He then converts them to a form to be passed as
        the method= parameter, and goes from there.

        http://micampe.it/things/flickrclient

        My variant is the same basic thing, except it tracks if it has
        already created a handler for a specific call or not.

        example usage:

            flickr.auth_getFrob(apiKey="AAAAAA")
            rsp = flickr.favorites_getList(apiKey=flickrAPIKey, \\
                auth_token=token)

        """

        # Refuse to act as a proxy for unimplemented special methods
        if method.startswith('__'):
            raise AttributeError("No such attribute '%s'" % method)

        if self.__handlerCache.has_key(method):
            # If we already have the handler, return it
            return self.__handlerCache.has_key(method)
        
        # Construct the method anem and URL only once for each handler.
        method = "flickr." + method.replace("_", ".")
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrRESTForm

        def handler(**args):
            '''Dynamically created handler for a Flickr API call'''
            
            LOG.debug("Calling %s(%s)" % (method, args))

            args["method"] = method
            postData = urllib.urlencode(args) + "&api_sig=" + self.__sign(args)

            f = urllib.urlopen(url, postData)
            data = f.read()
            f.close()
            
            return XMLNode.parseXML(data, True)

        self.__handlerCache[method] = handler

        return self.__handlerCache[method]
    
    #-------------------------------------------------------------------
    def __getAuthURL(self, perms, frob):
        """Return the authorization URL to get a token.

        This is the URL the app will launch a browser toward if it
        needs a new token.
            
        perms -- "read", "write", or "delete"
        frob -- picked up from an earlier call to FlickrAPI.auth_getFrob()

        """

        data = {"api_key": self.apiKey, "frob": frob, "perms": perms}
        data["api_sig"] = self.__sign(data)
        return "http://%s%s?%s" % (FlickrAPI.flickrHost, \
            FlickrAPI.flickrAuthForm, urllib.urlencode(data))

    #-------------------------------------------------------------------
    def upload(self, filename=None, jpegData=None, **arg):
        """Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        One of filename or jpegData must be specified by name when 
        calling this method:

        filename -- name of a file to upload
        jpegData -- array of jpeg data to upload

        api_key
        auth_token
        title
        description
        tags -- space-delimited list of tags, "tag1 tag2 tag3"
        is_public -- "1" or "0"
        is_friend -- "1" or "0"
        is_family -- "1" or "0"

        """

        if filename == None and jpegData == None or \
            filename != None and jpegData != None:

            raise IllegalArgumentException("filename OR jpegData must be specified")

        # verify key names
        for a in arg.keys():
            if a != "api_key" and a != "auth_token" and a != "title" and \
                a != "description" and a != "tags" and a != "is_public" and \
                a != "is_friend" and a != "is_family":

                sys.stderr.write("FlickrAPI: warning: unknown parameter " \
                    "\"%s\" sent to FlickrAPI.upload\n" % (a))
        
        arg["api_sig"] = self.__sign(arg)
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrUploadForm

        # construct POST data
        boundary = mimetools.choose_boundary()
        body = ""

        # required params
        for a in ('api_key', 'auth_token', 'api_sig'):
            body += "--%s\r\n" % (boundary)
            body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
            body += "%s\r\n" % (arg[a])

        # optional params
        for a in ('title', 'description', 'tags', 'is_public', \
            'is_friend', 'is_family'):

            if arg.has_key(a):
                body += "--%s\r\n" % (boundary)
                body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
                body += "%s\r\n" % (arg[a])

        body += "--%s\r\n" % (boundary)
        body += "Content-Disposition: form-data; name=\"photo\";"
        body += " filename=\"%s\"\r\n" % filename
        body += "Content-Type: image/jpeg\r\n\r\n"

        #print body

        if filename != None:
            fp = file(filename, "rb")
            data = fp.read()
            fp.close()
        else:
            data = jpegData

        postData = body.encode("utf_8") + data + \
            ("\r\n--%s--" % (boundary)).encode("utf_8")

        request = urllib2.Request(url)
        request.add_data(postData)
        request.add_header("Content-Type", \
            "multipart/form-data; boundary=%s" % boundary)
        response = urllib2.urlopen(request)
        rspXML = response.read()

        return XMLNode.parseXML(rspXML)

    #-------------------------------------------------------------------
    def replace(self, filename=None, jpegData=None, **arg):
        """Replace an existing photo.

        Supported parameters:

        One of filename or jpegData must be specified by name when 
        calling this method:

        filename -- name of a file to upload
        jpegData -- array of jpeg data to upload
        photo_id -- the ID of the photo to replace

        api_key
        auth_token
        """
        
        if (not filename and not jpegData) or (filename and jpegData):
            raise IllegalArgumentException("filename OR jpegData must be specified")

        # verify key names
        known_keys = ('api_key', 'auth_token', 'filename', 'jpegData',
                'photo_id')
        for a in arg.keys():
            if a not in known_keys:
                sys.stderr.write("FlickrAPI: warning: unknown parameter " \
                    "\"%s\" sent to FlickrAPI.replace\n" % (a))
        
        arg["api_sig"] = self.__sign(arg)
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrReplaceForm

        # construct POST data
        boundary = mimetools.choose_boundary()
        body = ""

        # required params
        for a in ('api_key', 'auth_token', 'api_sig', 'photo_id'):
            if a not in arg:
                raise IllegalArgumentException('Missing required argument %s' %
                        a)
            body += "--%s\r\n" % (boundary)
            body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
            body += "%s\r\n" % (arg[a])

        body += "--%s\r\n" % (boundary)
        body += "Content-Disposition: form-data; name=\"photo\";"
        body += " filename=\"%s\"\r\n" % filename
        body += "Content-Type: image/jpeg\r\n\r\n"

        if filename:
            fp = file(filename, "rb")
            data = fp.read()
            fp.close()
        else:
            data = jpegData

        postData = body.encode("utf_8") + data + \
            ("\r\n--%s--" % (boundary)).encode("utf_8")

        request = urllib2.Request(url)
        request.add_data(postData)
        request.add_header("Content-Type", \
            "multipart/form-data; boundary=%s" % boundary)
        response = urllib2.urlopen(request)
        rspXML = response.read()

        return XMLNode.parseXML(rspXML)


    #-----------------------------------------------------------------------
    @classmethod
    def testFailure(cls, rsp, exit_on_error=True):
        """Exit app if the rsp XMLNode indicates failure."""
        if rsp['stat'] == "fail":
            sys.stderr.write("%s\n" % (cls.getPrintableError(rsp)))
            if exit_on_error: sys.exit(1)

    #-----------------------------------------------------------------------
    @classmethod
    def getPrintableError(cls, rsp):
        """Return a printed error message string."""
        return "%s: error %s: %s" % (rsp.elementName, \
            cls.getRspErrorCode(rsp), cls.getRspErrorMsg(rsp))

    #-----------------------------------------------------------------------
    @classmethod
    def getRspErrorCode(cls, rsp):
        """Return the error code of a response, or 0 if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['code']

        return 0

    #-----------------------------------------------------------------------
    @classmethod
    def getRspErrorMsg(cls, rsp):
        """Return the error message of a response, or "Success" if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['msg']

        return "Success"

    #-----------------------------------------------------------------------
    def validateFrob(self, frob, perms, browser, fork):
        auth_url = self.__getAuthURL(perms, frob)
        
        if fork:
            if os.fork():
                return
        
            os.execlp(browser, browser, auth_url)
            raise SystemExit("Error starting browser, sorry")
        
        os.system("%s '%s'" % (browser, auth_url))

    #-----------------------------------------------------------------------
    def getTokenPartOne(self, perms="read", browser="firefox", fork=True):
        """Get a token either from the cache, or make a new one from the
        frob.
        
        This first attempts to find a token in the user's token cache on
        disk. If that token is present and valid, it is returned by the
        method.
        
        If that fails (or if the token is no longer valid based on
        flickr.auth.checkToken) a new frob is acquired.  The frob is
        validated by having the user log into flickr (with a browser).
        
        If the browser needs to take over the terminal, use fork=False,
        otherwise use fork=True.
        
        To get a proper token, follow these steps:
            - Store the result value of this method call
            - Give the user a way to signal the program that he/she has
              authorized it, for example show a button that can be
              pressed.
            - Wait for the user to signal the program that the
              authorization was performed, but only if there was no
              cached token.
            - Call flickrapi.getTokenPartTwo(...) and pass it the result
              value you stored.

        The newly minted token is then cached locally for the next run.

        perms--"read", "write", or "delete"
        browser--whatever browser should be used in the system() call             
    
        An example:
        
        (token, frob) = flickr.getTokenPartOne(perms='write')
        if not token: raw_input("Press ENTER after you authorized this program")
        token = flickr.getTokenPartTwo((token, frob))
        """
        
        # see if we have a saved token
        token = self.token_cache.token
        frob = None

        # see if it's valid
        if token:
            rsp = self.auth_checkToken(api_key=self.apiKey, auth_token=token)
            if rsp['stat'] != "ok":
                token = None
            else:
                # see if we have enough permissions
                tokenPerms = rsp.auth[0].perms[0].elementText
                if tokenPerms == "read" and perms != "read": token = None
                elif tokenPerms == "write" and perms == "delete": token = None

        # get a new token if we need one
        if not token:
            # get the frob
            rsp = self.auth_getFrob(api_key=self.apiKey)
            self.testFailure(rsp)

            frob = rsp.frob[0].elementText

            # validate online
            self.validateFrob(frob, perms, browser, fork)

        return (token, frob)
        
    def getTokenPartTwo(self, (token, frob)):
        """Part two of getting a token, see getTokenPartOne(...) for details."""

        # If a valid token was obtained, we're done
        if token:
            return token
        
        # get a token
        rsp = self.auth_getToken(api_key=self.apiKey, frob=frob)
        self.testFailure(rsp)

        token = rsp.auth[0].token[0].elementText

        # store the auth info for next time
        self.token_cache.token = rsp.xml

        return token

    #-----------------------------------------------------------------------
    def getToken(self, perms="read", browser="lynx"):
        """Get a token either from the cache, or make a new one from the
        frob.

        This first attempts to find a token in the user's token cache on
        disk.
        
        If that fails (or if the token is no longer valid based on
        flickr.auth.checkToken) a new frob is acquired.  The frob is
        validated by having the user log into flickr (with lynx), and
        subsequently a valid token is retrieved.

        The newly minted token is then cached locally for the next run.

        perms--"read", "write", or "delete"
        browser--whatever browser should be used in the system() call

        Use this method if you're sure that the browser process ends
        when the user has granted the autorization - not sooner and
        not later.
        """
        
        (token, frob) = self.getTokenPartOne(perms, browser, False)
        return self.getTokenPartTwo((token, frob))


########################################################################
# App functionality
########################################################################

def main():
    # flickr auth information:
    flickrAPIKey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # API key
    flickrSecret = "yyyyyyyyyyyyyyyy"                  # shared "secret"

    # make a new FlickrAPI instance
    fapi = FlickrAPI(flickrAPIKey, flickrSecret)

    # do the whole whatever-it-takes to get a valid token:
    token = fapi.getToken(browser="firefox")

    # get my favorites
    rsp = fapi.favorites_getList(api_key=flickrAPIKey,auth_token=token)
    fapi.testFailure(rsp)

    # and print them
    for a in rsp.photos[0].photo:
        print "%10s: %s" % (a['id'], a['title'].encode("ascii", "replace"))

    # upload the file foo.jpg
    #rsp = fapi.upload(filename="foo.jpg", \
    #   api_key=flickrAPIKey, auth_token=token, \
    #   title="This is the title", description="This is the description", \
    #   tags="tag1 tag2 tag3", is_public="1")
    #if rsp == None:
    #   sys.stderr.write("can't find file\n")
    #else:
    #   fapi.testFailure(rsp)

    return 0

# run the main if we're not being imported:
if __name__ == "__main__":
    sys.exit(main())

