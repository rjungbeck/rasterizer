import argparse
import datetime
import tempfile
import sys
import os
import shlex

from createprn import printToFile
from rll import RllConvert

from PIL import Image,PcxImagePlugin	

from mupdf import MuPdf
from serve import serve
	
SCALE=300.0/72.0
		
class PipeProducer(object):
	def __init__(self, globalParms):
		self.globalParms=globalParms
		
	def getTmpName(self, prefix, suffix):
		if prefix==None or prefix.startswith("*") or prefix=="":
			f=tempfile.NamedTemporaryFile(delete=False,prefix=self.req.tmpPrefix, suffix="."+suffix, dir=os.getcwd())
			ret=f.name
			f.close()
		else:
			ret="%s%d%s"%(prefix, self.curPage, suffix)
		return ret
			
	def producePage(self):
		self.muPdf.loadPage(self.curPage)
						
		pngName=self.getTmpName(self.req.pngPrefix, "png")
							
		self.muPdf.render(pngName, angle=self.req.angle, resolution=self.req.resolution, xDelta=self.req.xdelta, yDelta=self.req.ydelta, aaLevel=self.req.aalevel)
		self.muPdf.freePage()
		
		if self.req.pcxPrefix:
			pcxName=self.getTmpName(self.req.pcxPrefix, "pcx")
			
			im=Image.open(pngName)
			im.save(pcxName)
			if not self.req.keep:
				os.unlink(pngName)
			return pcxName
			
		if self.req.rllPrefix:
			rllName=self.getTmpName(self.req.rllPrefix, "rll")
			RllConvert(pngName, rllName)
			if not self.req.keep:
				os.unlink(pngName)
			return rllName
			
		if self.req.printer:
			prnName=self.getTmpName(self.req.prnPrefix, "prn")
			if printToFile(pngName, self.req.printer, prnName):
				if not self.req.keep:
					os.unlink(pngName)
				return prnName
			else:
				return ""
		return pngName

	
	def pipeMain(self):
		try:
			self.muPdf=MuPdf()
			curVersion=None
			curSource=None
			
			parser=argparse.ArgumentParser(description="PDF Pipe Renderer", epilog="(C) Copyright 2013 by RSJ Software GmbH Germering. All rights reserved. Licensed under AGPL V3", fromfile_prefix_chars="@")
			parser.add_argument("--angle", type=int, default=self.globalParms.angle, help="Rotation angle. Default: -90")
			parser.add_argument("--resolution", type=int, default=self.globalParms.resolution, help="Resolution in dpi. Default: 300")
			parser.add_argument("--printer", type=str, default=self.globalParms.printer, help="Printer name")
			parser.add_argument("--page", type=int, default=self.globalParms.page,help="Page number (1-based). Default: 1")
			parser.add_argument("--pdf", type=argparse.FileType(mode="rb"), help="PDF file")
			parser.add_argument("--exit", type=bool, default=False, help="Exit")
			parser.add_argument("--pngPrefix", type=str, default=self.globalParms.pngPrefix, help="PNG prefix")
			parser.add_argument("--prnPrefix", type=str, default=self.globalParms.prnPrefix, help="PRN prefix")
			parser.add_argument("--tmpPrefix", type=str, default=self.globalParms.tmpPrefix,  help="Temp prefix")
			parser.add_argument("--pcxPrefix", type=str, default=self.globalParms.pcxPrefix, help="PCX prefix")
			parser.add_argument("--rllPrefix", type=str, default=self.globalParms.rllPrefix, help="RLL prefix")
			parser.add_argument("--version", type=str, default="", help="Pdf Version")
			parser.add_argument("--noauto", type=bool, default=False, help="No automatic advance to next page")
			parser.add_argument("--keep", type=bool, default=self.globalParms.keep, help="Keep PNG")
			parser.add_argument("--xdelta", type=int, default=self.globalParms.xdelta, help="xDelta in px")
			parser.add_argument("--ydelta", type=int, default=self.globalParms.ydelta, help="yDelta in px")
			parser.add_argument("--aalevel", type=int, default=self.globalParms.aalevel, help="Anti aliasing level")
			
			while True:
				reqString=sys.stdin.readline()
				self.req=parser.parse_args(shlex.split(reqString))
				
				if self.req.exit:
					break
					
				if  curVersion!=self.req.version:
					self.muPdf.close()
					
					self.muPdf.load(self.req.pdf.read())
						
					count=self.muPdf.getPageCount()
					curVersion=self.req.version
					self.curPage=None
				
				if self.req.noauto or self.req.page!=self.curPage:
					if self.req.page <=count:
						self.curPage=self.req.page
						result=self.producePage()
					else:
						result=""

				sys.stdout.write(result+"\n")
				sys.stdout.flush()
				
				if not self.req.noauto:
					
					if self.req.page+1<=count:
						self.curPage=self.req.page+1
						result=self.producePage()
		except EOFError:
			pass
		
def main():
	parser=argparse.ArgumentParser(description="PDF Renderer", epilog="(C) Copyright 2013-2014 by RSJ Software GmbH Germering. All rights reserved. Licensed under AGPL V3", fromfile_prefix_chars="@")
	subparsers=parser.add_subparsers(help="Subcommands")
	
	parserPipe=subparsers.add_parser("pipe", help="Start as pipe server")
	parserPipe.add_argument("--angle", type=int, default=-90, help="Rotation angle. Default: -90")
	parserPipe.add_argument("--resolution", type=int, default=300, help="Resolution in dpi. Default: 300")
	parserPipe.add_argument("--printer", type=str, default="Zebra 170XiII", help="Printer name")
	parserPipe.add_argument("--page", type=int, default=1,help="Page number (1-based). Default: 1")
	parserPipe.add_argument("--pngPrefix", type=str, default=None, help="PNG prefix")
	parserPipe.add_argument("--prnPrefix", type=str, default=None, help="PRN prefix")
	parserPipe.add_argument("--tmpPrefix", type=str, default=None, help="Temp prefix")
	parserPipe.add_argument("--pcxPrefix", type=str, default=None, help="PCX prefix")
	parserPipe.add_argument("--rllPrefix", type=str, default=None, help="RLL prefix")	
	parserPipe.add_argument("--keep", type=bool, default=False, help="Keep PNG")
	parserPipe.add_argument("--xdelta", type=int, default=0, help="xDelta in px")
	parserPipe.add_argument("--ydelta", type=int, default=0, help="yDelta in px")
	parserPipe.add_argument("--aalevel", type=int, default=-1, help="Anti aliasing level")
	parserPipe.set_defaults(func=pipe)
	
	parserConvert=subparsers.add_parser("convert", help="Convert file")
	parserConvert.add_argument("--angle", type=int, default=-90, help="Rotation angle")
	parserConvert.add_argument("--resolution", type=int, default=300, help="Resolution in dpi")
	parserConvert.add_argument("--xdelta", type=int, default=0, help="xDelta in px")
	parserConvert.add_argument("--ydelta", type=int, default=0, help="yDelta in px")
	parserConvert.add_argument("--maxWidth", type=int, default=0, help="Max width in px")
	parserConvert.add_argument("--maxHeight", type=int, default=0, help="Max height in px")
	parserConvert.add_argument("--colorSpace", type=str, default="DeviceGray",help="Color space")
	parserConvert.add_argument("--aalevel", type=int, default=-1, help="Anti aliasing level")
	parserConvert.add_argument("--prnPrefix", type=str,  default=None, help="Output PRN prefix")
	parserConvert.add_argument("--pcxPrefix", type=str, default=None, help="Output PCX prefix")
	parserConvert.add_argument("--rllPrefix", type=str, default=None, help="Output RLL prefix")
	parserConvert.add_argument("--printer", type=str, default="Zebra 170XiII", help="Printer name")
	parserConvert.add_argument("inPdf", type=str, help="Input PDF file")
	parserConvert.add_argument("outPng", type=str, help="Output PNG prefix")
	parserConvert.set_defaults(func=convert)
	
	parserServe=subparsers.add_parser("serve", help="Serve")
	parserServe.add_argument("--port", type=int, default=8080, help="Server port")
	parserServe.set_defaults(func=serve)
	
	parms=parser.parse_args()
	parms.func(parms)
	
def pipe(parms):
	
	producer=PipeProducer(parms)
	producer.pipeMain()
		
def convert(parms):
	
	start=datetime.datetime.utcnow()
	muPdf=MuPdf()
	muPdf.open(parms.inPdf)
	count=muPdf.getPageCount()
	for i in range(1, count+1):
		muPdf.loadPage(i)
		pngName="%s%d.png" %(parms.outPng,i)
		muPdf.render(pngName,angle=parms.angle, resolution=parms.resolution, xDelta=parms.xdelta, yDelta=parms.ydelta, aaLevel=parms.aalevel,maxWidth=parms.maxWidth, maxHeight=parms.maxHeight, colorSpace=parms.colorSpace)
		if parms.pcxPrefix:
			im=Image.open(pngName)
			pcxName="%s%d.pcx" %(parms.pcxPrefix,i)
			print pcxName
			im.save(pcxName)
			
		if parms.rllPrefix:
			rllName="%s%d.rll" %(parms.rllPrefix,i)
			print rllName
			RllConvert(pngName, rllName)
			
		if parms.prnPrefix:
			prnName="%s%d.prn"%(parms.prnPrefix, i)
			if parms.printer:
				printToFile(pngName, parms.printer, prnName,)
	muPdf.freePage()
	muPdf.close()
	muPdf.freeContext()
	
	end=datetime.datetime.utcnow()
	print end-start
	
if __name__=="__main__":
	main()
