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
						<label for="pdf">PDF File</label>
						<input type="file" name="pdf"></input>
						<br>
						<label for="page">Page</label>
						<input type="number" name="page" value="1"></input>
						<br>
						<label for="maxWidth">Maximum Width</label>
						<input type="number" name="maxWidth"></input>
						<br>
						<label for="maxHeight">Maximum Height</label>
						<input type="number" name="maxHeight"></input>
						<br>
						<input type="submit" name="Submit"></input>
					</form>
					<p>You can can find the (AGPL 3 licensed) rasterizer source code on <a href="https://github.com/rjungbeck/rasterizer">https://github.com/rjungbeck/rasterizer</a>.</p>
				</body>
			</html>
			""")
		
	def post(self):
		muPdf=mupdf.MuPdf()
		muPdf.load(self.request.POST.get('pdf').file.read())
		try:
			page=int(self.request.get("page"))
		except:
			page=1
			pass
		try:
			maxWidth=int(self.request.get("maxWidth"))
		except:
			maxWidth=None
			pass
		try:
			maxHeight=int(self.request.get("maxHeight"))
		except:
			maxHeight=None
			pass
		muPdf.loadPage(page)
		targetName=str(uuid.uuid4())+".png"
		muPdf.render(targetName,colorSpace="DeviceRGB", maxWidth=maxWidth, maxHeight=maxHeight)
		muPdf.freePage()
		muPdf.close()
		muPdf.freeContext()
		self.response.headers['Content-Type'] = "image/png"
		with open(targetName,"rb") as pngFile:
			self.response.out.write(pngFile.read())
		os.unlink(targetName)
		