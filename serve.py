import uuid
import os

from twisted.web import server, resource, static, iweb
from twisted.internet import defer,reactor
from twisted.web.wsgi import WSGIResource

import webapp2

import mupdf

mapping=[
	("/", "serve.MainHandler"),
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

class MainHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("""
			<html>
				<body>
					<h1>Rasterizer Web Service</h1>
					<p>You can can find the (AGPL 3 licensed) rasterizer source code on <a href="https://github.com/rjungbeck/rasterizer">https://github.com/rjungbeck/rasterizer</a>.</p>
				</body>
			</html>
			""")

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
						<input type="number" name="maxWidth" value="1000"></input>
						<br>
						<label for="maxHeight">Maximum Height</label>
						<input type="number" name="maxHeight" value="1000"></input>
						<br>
						<label for="angle">Angle</label>
						<input type="number" name="angle" value="0"></input>
						
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
		
		try:
			maxWidth=int(self.request.get("maxWidth"))
		except:
			maxWidth=None
		
		try:
			maxHeight=int(self.request.get("maxHeight"))
		except:
			maxHeight=None
			
		try:
			angle=int(self.request.get("angle"))
		except:
			angle=0

		try:
			x0=float(self.request.get("x0"))
			y0=float(self.request.get("y0"))
			x1=float(self.request.get("x1"))
			y1=float(self.request.get("y1"))
		except:
			x0=0.0
			x1=0.0
			y0=0.0
			y1=0.0
		muPdf.loadPage(page)
		targetName=str(uuid.uuid4())+".png"
		muPdf.render(targetName,colorSpace="DeviceRGB", maxWidth=maxWidth, maxHeight=maxHeight, angle=angle, x0=x0, y0=y0, x1=x1, y1=y1)
		muPdf.freePage()
		muPdf.close()
		muPdf.freeContext()
		self.response.headers['Content-Type'] = "image/png"
		with open(targetName,"rb") as pngFile:
			self.response.out.write(pngFile.read())
		os.unlink(targetName)
