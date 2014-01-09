import uuid
import os

from twisted.web import server, resource, static, iweb
from twisted.internet import defer,reactor
from twisted.web.wsgi import WSGIResource

import webapp2	

import mupdf

mapping=[
	("/convert", "serve.ConvertHandler")
	]
	
def serve(parms):
	
	app = webapp2.WSGIApplication(mapping, debug=True)

	wsgiResource=WSGIResource(reactor, reactor.getThreadPool(), app)
		
	thisSite=server.Site(wsgiResource)
	reactor.listenTCP(parms.port, thisSite)
	reactor.run()
	
def stop():
	reactor.stop()
	
class ConvertHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("""
			<html>
				<body>
					<h1>Rasterizer</h1>
					<form method="POST" enctype="multipart/form-data">
						<input type="file" name="pdf"></input>
						<input type="number" name="page" vaue="1"></input>
						<input type="submit" name="Submit"></input>
					</form>
					<p>You can can find the (AGPL 3 licensed)m rasterizer source code on <a href="https://github.com/rjungbeck/rasterizer">https://github.com/rjungbeck/rasterizer</a>.</p>
				</body>
			</html>
			""")
		
	def post(self):
		muPdf=mupdf.MuPdf()
		muPdf.load(self.request.POST.get('pdf').file.read())
		page=int(self.request.get("page"))
		muPdf.loadPage(page)
		targetName=str(uuid.uuid4())+".png"
		muPdf.render(targetName,colorSpace="DeviceRGB")
		muPdf.freePage()
		muPdf.close()
		muPdf.freeContext()
		self.response.headers['Content-Type'] = "image/png"
		with open(targetName,"rb") as pngFile:
			self.response.out.write(pngFile.read())
		os.unlink(targetName)
		