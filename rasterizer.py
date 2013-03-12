import argparse
import datetime
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER
import tempfile
import sys
import os
import shlex

from createprn import printToFile

class Matrix(Structure):
	_fields_=[("a", c_float),("b", c_float),("c", c_float),("d", c_float),("e", c_float),("f", c_float)]

class Rect(Structure):
	_fields_=[("x0", c_float), ("y0", c_float), ("x1", c_float), ("y1", c_float)]
	
class BBox(Structure):
	_fields_=[("x0", c_int), ("y0", c_int), ("x1", c_int), ("y1", c_int)]
	
	
FZ_STORE_UNLIMITED=0
SCALE=300.0/72.0

class MuPdf():
	def __init__(self):
		self.dll=cdll.libmupdf
		self.dll.fz_scale.argtypes=[POINTER(Matrix), c_float, c_float]
		self.dll.fz_scale.restype=POINTER(Matrix)
		
		self.dll.fz_rotate.argtypes=[POINTER(Matrix), c_float]
		self.dll.fz_rotate.restype=POINTER(Matrix)
		
		self.dll.fz_concat.argtypes=[POINTER(Matrix), POINTER(Matrix), POINTER(Matrix)]
		self.dll.fz_concat.restype=POINTER(Matrix)
		
		self.dll.fz_bound_page.argtypes=[c_void_p, c_void_p, POINTER(Rect)]
		self.dll.fz_bound_page.restype=POINTER(Rect)
		
		self.dll.fz_transform_rect.argtypes=[POINTER(Rect), POINTER(Matrix)]
		self.dll.fz_transform_rect.restype=POINTER(Rect)
		
		self.dll.fz_round_rect.argtypes=[POINTER(BBox), POINTER(Rect)]
		self.dll.fz_round_rect.restype=POINTER(BBox)
		
		self.dll.fz_new_pixmap_with_bbox.argtypes=[c_void_p, c_void_p, POINTER(BBox)]
		self.dll.fz_new_pixmap_with_bbox.restype=c_void_p
		
		self.dll.fz_run_page.argtypes=[c_void_p, c_void_p, c_void_p, POINTER(Matrix), c_void_p]
		self.dll.fz_run_page.restype=None
		
		self.dll.fz_open_document.argtypes=[c_void_p, c_char_p]
		self.dll.fz_open_document.restype=c_void_p
		
		self.dll.fz_open_document_with_stream.argtypes=[c_void_p, c_char_p, c_void_p]
		self.dll.fz_open_document_with_stream.restype=c_void_p
		
		self.dll.fz_close_document.argtypes=[c_void_p]
		self.dll.fz_close_document.restype=None
		
		self.dll.fz_count_pages.argtypes=[c_void_p]
		self.dll.fz_count_pages.restype=c_int
		
		self.dll.fz_find_device_colorspace.argtypes=[c_void_p, c_char_p]
		self.dll.fz_find_device_colorspace.restype=c_void_p
		
		self.dll.fz_clear_pixmap_with_value.argtypes=[c_void_p, c_void_p, c_int]
		self.dll.fz_clear_pixmap_with_value.restype=None
		
		self.dll.fz_new_draw_device.argtypes=[c_void_p, c_void_p]
		self.dll.fz_new_draw_device.restype=c_void_p
		
		self.dll.fz_free_device.argtyppes=[c_void_p]
		self.dll.fz_free_device.restype=None
		
		self.dll.fz_write_png.argtypes=[c_void_p, c_void_p, c_char_p, c_int]
		self.dll.fz_write_png.restype=None
		
		self.dll.fz_drop_pixmap.argtypes=[c_void_p, c_void_p]
		self.dll.fz_drop_pixmap.restype=None
		
		self.dll.fz_free_page.argtypes=[c_void_p, c_void_p]
		self.dll.fz_free_page.restype=None
		
		self.dll.fz_free_context.argtypes=[c_void_p]
		self.dll.fz_free_context.restype=None
		
		self.dll.fz_open_memory.argtypes=[c_void_p, c_char_p, c_int]
		self.dll.fz_open_memory.restype=c_void_p
		
		self.dll.fz_close.argtypes=[c_void_p]
		self.dll.fz_close.restype=None
		
		self.stream=None
		self.doc=None
		
		self.context=self.dll.fz_new_context(None, None, FZ_STORE_UNLIMITED)
			
	def open(self, name):
		with open(name, "rb") as f:
			self.content=f.read()
			self.load(self.content)
			
	def load(self, content):
		self.content=content
		if self.context==None:
			self.context=self.dll.fz_new_context(None, None, FZ_STORE_UNLIMITED)
	
		self.stream=self.dll.fz_open_memory(self.context, self.content, len(self.content))
		self.doc=self.dll.fz_open_document_with_stream(self.context, "application/pdf", self.stream)
		
		#self.doc=self.dll.fz_open_document(self.context, name)
		
	def getPageCount(self):
		return self.dll.fz_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.fz_load_page(self.doc, num-1)
		
	def render(self,name,angle=0,resolution=300.0):
		transform=Matrix()
		self.dll.fz_scale(transform, resolution/72.0, resolution/72.0)
		transform1=Matrix()
		transform2=Matrix()
		self.dll.fz_rotate(transform2, angle)
		self.dll.fz_concat(transform1, transform, transform2) 
		rect=Rect()
		self.dll.fz_bound_page(self.doc, self.page,rect)
		self.dll.fz_transform_rect(rect, transform1)
		bbox=BBox()
		self.dll.fz_round_rect(bbox,rect)
		fz_device_rgb=self.dll.fz_find_device_colorspace(self.context, "DeviceGray")
		pix=self.dll.fz_new_pixmap_with_bbox(self.context, fz_device_rgb, bbox)
		self.dll.fz_clear_pixmap_with_value(self.context, pix, 255)
		dev=self.dll.fz_new_draw_device(self.context, pix)
		self.dll.fz_run_page(self.doc, self.page, dev, transform1, None)
		self.dll.fz_free_device(dev)
		dev=None
		self.dll.fz_write_png(self.context, pix, name, 0)
		self.dll.fz_drop_pixmap(self.context, pix)
		pix=None
		
	def freePage(self):
		self.dll.fz_free_page(self.doc, self.page)
		self.page=None
		
	def close(self):
		if self.stream:
			self.dll.fz_close(self.stream)
			self.stream=None
		if self.doc:
			self.dll.fz_close_document(self.doc)
			self.doc=None
		
	def freeContext(self):
		if self.context:
			self.dll.fz_free_context(self.context)
			self.context=None
		
class PipeProducer():
	def __init__(self, globalParms):
		self.globalParms=globalParms
	
	def producePage(self):
		self.muPdf.loadPage(self.curPage)
						
		if self.req.pngPrefix:
			pngName="%s%d.png" %(self.req.pngPrefix, self.curPage)
		else:
			f=tempfile.NamedTemporaryFile(delete=False,prefix=self.req.tmpPrefix, suffix=".png")
			pngName=f.name
			f.close()
							
		self.muPdf.render(pngName, angle=self.req.angle, resolution=self.req.resolution)
		self.muPdf.freePage()
						
		if self.req.printer:
			if self.req.prnPrefix:
				prnName="%d%d%.prn"%(self.req.prnPrefix, self.curPage)
			else:
				f=tempfile.NamedTemporaryFile(delete=False, prefix=self.req.tmpPrefix, suffix=".prn")
				prnName=f.name
				f.close()
			if printToFile(pngName, self.req.printer, prnName):
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
			
			parser=argparse.ArgumentParser(description="PDF Pipe Renderer", epilog="(C)Copyright 2013 by RSJ Software GmbH Germering. All rights reserved. Licensed under AGPL V3", fromfile_prefix_chars="@")
			parser.add_argument("--angle", type=int, default=self.globalParms.angle, help="Rotation angle. Default: -90")
			parser.add_argument("--resolution", type=int, default=self.globalParms.resolution, help="Resolution in dpi. Default: 300")
			parser.add_argument("--printer", type=str, default=self.globalParms.printer, help="Printer name")
			parser.add_argument("--page", type=int, default=self.globalParms.page,help="Page number (1-based). Default: 1")
			parser.add_argument("--pdf", type=argparse.FileType(mode="rb"), help="PDF file")
			parser.add_argument("--exit", type=bool, default=False, help="Exit")
			parser.add_argument("--pngPrefix", type=str, default=self.globalParms.pngPrefix, help="PNG prefix")
			parser.add_argument("--prnPrefix", type=str, default=self.globalParms.prnPrefix, help="PRN prefix")
			parser.add_argument("--tmpPrefix", type=str, default=self.globalParms.tmpPrefix,  help="Temp prefix")
			parser.add_argument("--version", type=str, default="", help="Pdf Version")
			parser.add_argument("--noauto", type=bool, default=False, help="No automatic advance to next page")
			
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
					
				if self.req.page!=self.curPage:
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
	parser=argparse.ArgumentParser(description="PDF Renderer", epilog="(C)Copyright 2013 by RSJ Software GmbH Germering. All rights reserved. Licensed under AGPL V3", fromfile_prefix_chars="@")
	subparsers=parser.add_subparsers(help="Subcommands")
	parserPipe=subparsers.add_parser("pipe", help="Start as pipe server")
	parserPipe.add_argument("--angle", type=int, default=-90, help="Rotation angle. Default: -90")
	parserPipe.add_argument("--resolution", type=int, default=300, help="Resolution in dpi. Default: 300")
	parserPipe.add_argument("--printer", type=str, default="Zebra 170XiII", help="Printer name")
	parserPipe.add_argument("--page", type=int, default=1,help="Page number (1-based). Default: 1")
	parserPipe.add_argument("--url", type=str, default=None, help="Download URL")
	parserPipe.add_argument("--pngPrefix", type=str, default=None, help="PNG prefix")
	parserPipe.add_argument("--prnPrefix", type=str, default=None, help="PRN prefix")
	parserPipe.add_argument("--tmpPrefix", type=str, default=None, help="Temp prefix")
	parserPipe.set_defaults(func=pipe)
	parserConvert=subparsers.add_parser("convert", help="Convert file")
	parserConvert.add_argument("--angle", type=int, default=-90, help="Rotation angle")
	parserConvert.add_argument("--resolution", type=int, default=300, help="Resolution in dpi")
	parserConvert.add_argument("inPdf", type=str, help="Input PDF file")
	parserConvert.add_argument("outPng", type=str, help="Output PNG prefix")
	parserConvert.add_argument("printer", type=str, default="Zebra 170XiII", help="Printer name")
	parserConvert.add_argument("prnPrefix", type=str,  help="Output PRN prefix")
	parserConvert.set_defaults(func=convert)
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
		muPdf.render(pngName,angle=parms.angle, resolution=parms.resolution)
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
