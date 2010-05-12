# -*- test-case-name: twisted.web.test.test_proxy -*-
# Copyright (c) 2001-2007 Twisted Matrix Laboratories.
# See LICENSE for details.


import urlparse
from urllib import quote as urlquote
from urllib import urlencode
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.http import HTTPClient, Request, HTTPChannel
from twisted.web.proxy import ProxyClient,ProxyClientFactory
from ratiomaster import webinterface,session


global trackersessions
trackersessions=session.TrackerSessions()
global userinterface
userinterface=webinterface.WebInterface(trackersessions)

class InterceptProxyRequest(Request):
    
    protocols = {'http': ProxyClientFactory}
    ports = {'http': 80}
    def manipulateQuery(self, query):
        pass
    
    def __webinterface(self):
        ret = userinterface.render(self)
        
        if not self.startedWriting and ret != NOT_DONE_YET:
            self.write(ret)
            self.finish()
    def __init__(self, channel, queued, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor = reactor



    #def process(self):
    #    s=scheduler.Scheduler(self._process())
    #    s.start() 

    def process(self):
		#log.msg("asdas")
        parsed = urlparse.urlparse(self.uri)
        #Is proxy request??
        #print self.uri
        if not self.uri[0:4] == "http":
            self.__webinterface()
            return
            #raise StopIteration
        protocol = parsed[0]
        host = parsed[1]
        port = self.ports[protocol]
        if ':' in host:
            host, port = host.split(':')
            port = int(port)

        class_ = self.protocols[protocol]
        headers = self.getAllHeaders().copy()
        if 'host' not in headers:
            headers['host'] = host
        self.content.seek(0, 0)
        s = self.content.read()
        query = urlparse.parse_qs(parsed[4])
        try:
            info_hash = query['info_hash'][0]
            uploaded = query['uploaded'][0]
            event = query.get('event', [''])[0]
        except: #not an announce request
            return
        try:
            ses = trackersessions.get(info_hash)
        except:
            ses = trackersessions.add(info_hash,event, uploaded, 0, hostname=host)
        ses.setState(event, uploaded)
        
        fakeuploaded = ses.getUploaded()
        query = urlparse.parse_qs(parsed[4])
        for i in query:
            query[i] = query[i][0]
        query['uploaded'] = fakeuploaded
        rest = urlparse.urlunparse(('','') + parsed[2:4] + (urlencode(query),) +parsed[5:])
        if not rest:
            rest = rest + '/'
        
        
        clientFactory = class_(self.method, rest, self.clientproto, headers, s, self)
        self.reactor.connectTCP(host, port, clientFactory)


class InterceptProxy(HTTPChannel):
    """
    This class implements a simple web proxy.

    Since it inherits from L{twisted.protocols.http.HTTPChannel}, to use it you
    should do something like this::

        from twisted.web import http
        f = http.HTTPFactory()
        f.protocol = Proxy

    Make the HTTPFactory a listener on a port as per usual, and you have
    a fully-functioning web proxy!
    """

    requestFactory = InterceptProxyRequest
