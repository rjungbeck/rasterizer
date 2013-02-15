import argparse
import datetime
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p
import os
import tempfile
import multiprocessing
import sys

import requests

from createprn import printToFile
import converter

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
		self.dll.fz_scale.argtypes=[c_float, c_float]
		self.dll.fz_scale.restype=Matrix
		
		self.dll.fz_rotate.argtypes=[c_float]
		self.dll.fz_rotate.restype=Matrix
		
		self.dll.fz_concat.argtypes=[Matrix, Matrix]
		self.dll.fz_concat.restype=Matrix
		
		self.dll.fz_bound_page.argtypes=[c_void_p, c_void_p]
		self.dll.fz_bound_page.restype=Rect
		
		self.dll.fz_transform_rect.argtypes=[Matrix, Rect]
		self.dll.fz_transform_rect.restype=Rect
		
		self.dll.fz_round_rect.argtypes=[Rect]
		self.dll.fz_round_rect.restype=BBox
		
		self.dll.fz_new_pixmap_with_bbox.argtypes=[c_int, c_int, BBox]
		self.dll.fz_new_pixmap_with_bbox.restype=c_void_p
		
		self.dll.fz_run_page.argtypes=[c_void_p, c_void_p, c_void_p, Matrix, c_void_p]
		self.dll.fz_run_page.restype=None
		
		self.dll.fz_open_document.argtypes=[c_void_p, c_char_p]
		self.dll.fz_open_document.restype=c_void_p
		
		self.dll.fz_open_document_with_stream.argtypes=[c_void_p, c_char_p, c_void_p]
		self.dll.fz_open_document_with_stream.restype=c_void_p
		
		self.dll.fz_close_document.argtypes=[c_void_p]
		self.dll.fz_close_document.restype=None
		
		self.dll.fz_count_pages.argtypes=[c_void_p]
		#self.dll.fz_count_pages.restype=c_int
		
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
		
		self.context=self.dll.fz_new_context(None, None, FZ_STORE_UNLIMITED)
			
	def open(self, name):
		with open(name, "rb") as f:
			self.content=f.read()
			self.load(self.content)
			
	def load(self, content):
		self.content=content
		self.stream=self.dll.fz_open_memory(self.context, self.content, len(self.content))
		self.doc=self.dll.fz_open_document_with_stream(self.context, "application/pdf", self.stream)
		
		#self.doc=self.dll.fz_open_document(self.context, name)
		
	def getPageCount(self):
		return self.dll.fz_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.fz_load_page(self.doc, num-1)
		
	def render(self,name,angle=0,resolution=300.0):
		transform=self.dll.fz_scale(resolution/72.0, resolution/72.0)
		transform=self.dll.fz_concat(transform, self.dll.fz_rotate(angle)) 
		rect=self.dll.fz_bound_page(self.doc, self.page)
		rect=self.dll.fz_transform_rect(transform, rect)
		bbox=self.dll.fz_round_rect(rect)
		fz_device_rgb=self.dll.fz_find_device_colorspace(self.context, "DeviceGray")
		pix=self.dll.fz_new_pixmap_with_bbox(self.context, fz_device_rgb, bbox)
		self.dll.fz_clear_pixmap_with_value(self.context, pix, 255)
		dev=self.dll.fz_new_draw_device(self.context, pix)
		self.dll.fz_run_page(self.doc, self.page, dev, transform, None)
		self.dll.fz_free_device(dev)
		dev=None
		self.dll.fz_write_png(self.context, pix, name, 0)
		self.dll.fz_drop_pixmap(self.context, pix)
		pix=None
		
	def freePage(self):
		self.dll.fz_free_page(self.doc, self.page)
		self.page=None
		
	def close(self):
		self.dll.fz_close(self.stream)
		self.dll.fz_close_document(self.doc)
		self.doc=None
		
	def freeContext(self):
		self.dll.fz_free_context(self.context)
		self.context=None
	
def pipeMain(pipe):
	try:
		muPdf=MuPdf()
		session=requests.Session()
		curVersion=None
		curSource=None
		
		parser=argparse.ArgumentParser(description="PDF Pipe Renderer", epilog="(C)Copyright 2013 by RSJ Software GmbH Germering. All rights reserved. Licensed under GPL V3", fromfile_prefix_chars="@")
		parser.add_argument("--angle", type=int, default=-90, help="Rotation angle. Default: -90")
		parser.add_argument("--resolution", type=int, default=300, help="Resolution in dpi. Default: 300")
		parser.add_argument("--printer", type=str, default="Zebra 170XiII", help="Printer name")
		parser.add_argument("--page", type=int, default=1,help="Page number (1-based). Default: 1")
		parser.add_argument("--url", type=str, help="Download URL")
		parser.add_argument("--pdf", type=argparse.FileType(mode="rb"), help="PDF file")
		parser.add_argument("--exit", type=bool, default=False, help="Exit")
		parser.add_argument("--pngPrefix", type=str, help="PNG prefix")
		parser.add_argument("--prnPrefix", type=str, help="PRN prefix")
		parser.add_argument("--version", type=str, default="", help="Pdf Version")
		
		while True:
			reqString=pipe.recv()
			req=parser.parse_args(reqString.split())
			
			if req.exit:
				break
				
			if curSource!=req.url or curVersion!=req.version:
				if req.url:
					curSource=req.url
					r=session.get(curSource)
					muPdf.load(r.content)
				elif req.pdf:
					muPdf.load(req.pdf.read())
					
				count=muPdf.getPageCount()
				curVersion=req.version
				curPage=None
				
			if req.page!=curPage:
				if req.page <count:
					curPage=req.page
					
					muPdf.loadPage(curPage)
					
					if req.pngPrefix:
						pngName="%s%d.png" %(req.pngPrefix, curPage)
					else:
						f=tempfile.NamedTemporaryFile(delete=False)
						pngName=f.name
						f.close()
						
					muPdf.render(pngName, angle=req.angle, resolution=req.resolution)
					
					if req.printer:
						if req.prnPrefix:
							prnName="%d%d%.prn"%(req.prnPrefix, curPage)
						else:
							f=tempfile.NamedTemporaryFile(delete=False)
							prnName=f.name
							f.close()
						printToFile(pngName, req.printer, prnName)
						os.unlink(pngName)
				else:
					prnName=""
					pngName=""
				
			if req.printer:
				pipe.send(prnName)
			else:
				pipe.send(pngName)
				
				if req.page+1<count:
					curPage=req.page+1
					muPdf.loadPage(curPage)
					if req.pngPrefix:
						pngName="%s%d.png" %(req.pngPrefix, curPage)
					else:
						pngName=os.tempnam()
					
					muPdf.render(pngName, angle=req.angle, resolution=req.resolution)
					if req.printer:
						if req.prnPrefix:
							prnName="%d%d%.prn"%(req.prnPrefix, curPage)
						else:
							prnName=os.tempnam()
					
						printToFile(pngName, req.printer, prnName)
						os.unlink(pngName)
	except EOFError:
		pass
		
def main():
	parser=argparse.ArgumentParser(description="PDF Renderer", epilog="(C)Copyright 2013 by RSJ Software GmbH Germering. All rights reserved. Licensed under GPL V3", fromfile_prefix_chars="@")
	parser.add_argument("--angle", type=int, default=-90, help="Rotation angle")
	parser.add_argument("--resolution", type=int, default=300, help="Resolution in dpi")
	parser.add_argument("inPdf", type=str, help="Input PDF file")
	parser.add_argument("outPng", type=str, help="Output PNG prefix")
	parser.add_argument("printer", type=str, default="Zebra 170XiII", help="Printer name")
	parser.add_argument("prnPrefix", type=str, help="Output PRN prefix")
	parms=parser.parse_args()
	
	start=datetime.datetime.utcnow()
	muPdf=MuPdf()
	muPdf.open(parms.inPdf)
	count=muPdf.getPageCount()
	for i in range(1, count+1):
		muPdf.loadPage(i)
		pngName="%s%d.png" %(parms.outPng,i)
		muPdf.render(pngName,angle=parms.angle, resolution=parms.resolution)
		prnName="%s%d.prn"%(parms.prnPrefix, i)
		printToFile(pngName, parms.printer, prnName,)
	muPdf.freePage()
	muPdf.close()
	muPdf.freeContext()
	
	end=datetime.datetime.utcnow()
	print end-start
	