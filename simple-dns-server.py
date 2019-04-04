#!/usr/bin/python

from twisted.internet import reactor, defer
from twisted.internet import task
from twisted.names import dns, error, server
from twisted.web import http
import random
import time;

#config
http_port   = 80
password    = 'kkkkkkkk'
names       = {}

class DynamicResolver(object):
	def _doDynamicResponse(self, query):
		print (query.name.name)
		if names.has_key(query.name.name):
			payload = dns.Record_A( names[query.name.name] , ttl = 60)

			answer  = dns.RRHeader(
				name=query.name.name ,
				payload=payload,
				type=dns.A,
				ttl = 60 ,
			)

			answers    = [answer]
			authority  = []
			additional = []

		return answers, authority, additional

	def query(self, query, timeout=None):
		print 'query'
		if query.type == dns.A :
			return defer.succeed(self._doDynamicResponse(query))
		else:
			return defer.fail(error.DomainError())



class MyRequestHandler(http.Request):
	resources={
		'/':"<h1>DNS Server</h1><p>/add?name=???&ip=???key=???<p>/del?name=???&key=???<p> current : <p>",
		}
	def process(self):
		self.setHeader('Content-Type','text/html')
		if self.path == '/':
			self.write( "%s%s" % (self.resources[self.path] , names.__str__() ) )

		elif self.path == '/del' : 
			key = self.args.get('key')
			if key[0] == password :
				name = self.args.get('name')
				del names[name[0]]
				self.write('del ok!')
			else:
				self.write('key error!')

		elif self.path == '/add' : 
			key = self.args.get('key')
			if key[0] == password :
				name = self.args.get('name')
				ip   = self.args.get('ip')
				names[name[0]] = ip[0]
				self.write('Add ok!')
			else:
				self.write('key error!')
		else:
			self.setResponseCode(http.NOT_FOUND)
			self.write("<h1>Not Found</h1>Sorry, no such source")
		self.finish()

class MyHTTP(http.HTTPChannel):
	requestFactory=MyRequestHandler

class MyHTTPFactory(http.HTTPFactory):
	def buildProtocol(self,addr):
		return MyHTTP()

def main():

	factory = server.DNSServerFactory(
		clients=[DynamicResolver()]
	)
	protocol = dns.DNSDatagramProtocol(controller=factory)
	reactor.listenUDP(53, protocol ,'10.255.175.85' )

	reactor.listenTCP(http_port,MyHTTPFactory())

	reactor.run()



if __name__ == '__main__':
	raise SystemExit(main())
