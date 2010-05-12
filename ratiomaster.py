from twisted.web import proxy, http
from twisted.internet import reactor
from ratiomaster import intercept
from twisted.web.proxy import Proxy
import sys

class ProxyFactory(http.HTTPFactory):
    protocol = intercept.InterceptProxy
 
reactor.listenTCP(8888, ProxyFactory(), interface='127.0.0.1')
reactor.run()
