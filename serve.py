import uuid
import os
import json
import uuid
import zipfile

from twisted.web import server, resource, static, iweb
from twisted.internet import defer,reactor
from twisted.web.wsgi import WSGIResource

import webapp2
import requests

import mupdf
import oauth2

mapping=[
	("/", "serve.MainHandler"),
	("/auth", "serve.AuthHandler"),
	("/convert", "serve.ConvertHandler"),
	("/batch", "serve.BatchHandler")
	]

config={}
accssToken=""

def serve(parms):
	global config
	
	with open(parms.config, "r") as configFile:
		config=json.load(configFile)
		
	global accessToken
	accessToken=str(uuid.uuid4())
		
	app = webapp2.WSGIApplication(mapping, debug=True)

	wsgiResource=WSGIResource(reactor, reactor.getThreadPool(), app)

	thisSite=server.Site(wsgiResource)
	
	if config["httpPort"]:
		reactor.listenTCP(config["httpPort"], thisSite)
		
	if config["httpsKey"]:
		from twisted.internet import ssl
		sslContext=ssl.DefaultOpenSSLContextFactory(config["httpsKey"], config["httpsCertificate"])
		reactor.listenSSL(config["httpsPort"], thisSite, sslContext)
		
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
		
oauth2Cache={}

class BatchHandler(webapp2.RequestHandler):
	def post(self):
		global oauth2Cache
		
		token=self.request.get("oauth_token")
		if not token:
			auth=self.request.headers["Authorization"]
			authParts=auth.split(2)
			token=authParts[1]
		if token!=accessToken:
			self.error(403)
			
		data=self.request.POST.get("zip").file
		with zipfile.ZipFile(dataFile, "r") as zip:
			meta=json.load(zip.open("batch.meta", "r"))
			pdf=zip.read("batch.pdf")
			
		muPdf=mupdf.MuPdf()
		muPdf.load(pdf)
		
		rsp=[]
		
		i=1
		for metaLabel in meta["labels"]:
			muPdf.loadPage(i)
			targetName=str(uuid.uuid4())+".png"
			muPdf.render(targetName, colorSpace=metaLabel["colorSpace"], maxWidth=metaLabel["maxWidth"], maxHeight=metalabel["maxHeight"])
			muPdf.freePage()
			station=metaLabel["station"]
			metaStation=meta[station]
			if not station in oauth2Cache:
				oauth2Cache[target]=oauth2.OAuth2(clientId=metaStation["clientId"], clientSecret=metaStation["clientSecret"], refreshToken=metaStation["refreshToken"], authUrl=metaStation["authUrl"])
				
			targetUrl=metaStation["baserUrl"]+metaLabel["tag"]
			png=""
			with open(targetName, "rb") as pngFile:
				png=pngFile.read()
			req=requests.post(targetUrl,files={"bitmap":png}, auth=oauth2Cache[station])
			if req.status_code==200:
				reply=req.json()
				reply["target"]=metaLabel["target"]
			else:
				reply={"error": rq.status_code, "target":metaLabel["target"]}
			rsp.append(reply)
				
			os.unlink(targetName)
			i+=1
			
		muPdf.close()
		muPdf.freeContect()
		
		self.response.headers["Content-Type"]="application/json"
		self.response.out.write(json.dumps(rsp))
		
class AuthHandler(webapp2.RequestHandler):
	def post(self):
		clientId=self.request.get("client_id")
		clientSecret=self.request.get("client_secret")
		refreshToken=self.request.get("refresh_token")
		
		if clientId in config["clients"]:
			if config["clients"][clientId]["clientSecret"]==clientSecret:
				if config["clients"][clientId]["refreshToken"]==refreshToken:
		
					rsp={"expires_in":360000, "access_token":accessToken}
					self.response.headers["Content-Type"]="application/json"
					self.respone.out.write(json.dumps(rsp))
					return
			
		self.error(403)
		