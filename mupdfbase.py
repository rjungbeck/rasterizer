from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER

import transform

FZ_STORE_UNLIMITED=0

class Matrix(Structure):
	_fields_=[("a", c_float),("b", c_float),("c", c_float),("d", c_float),("e", c_float),("f", c_float)]

class Rect(Structure):
	_fields_=[("x0", c_float), ("y0", c_float), ("x1", c_float), ("y1", c_float)]
	
class BBox(Structure):
	_fields_=[("x0", c_int), ("y0", c_int), ("x1", c_int), ("y1", c_int)]
	
class MuPdfBase(object):
	
	def __init__(self):
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
		
		self.dll.fz_set_aa_level.argtypes=[c_void_p, c_int]
		self.dll.fz_set_aa_level.restype=None
		
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
		
	def getPageCount(self):
		return self.dll.fz_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.fz_load_page(self.doc, num-1)
		
	def render(self,name,angle=0,resolution=300.0, xDelta=0.0, yDelta=0.0, aaLevel=-1,maxWidth=0, maxHeight=0, colorSpace="DeviceGray"):
		x0,y0,x1,y1=self.getSize()
		
		w=abs(x0-x1)*resolution/72.0
		h=abs(y0-y1)*resolution/72.0
		if angle==90 or angle==270 or angle==-90 or angle==-270:
			w,h=h,w
			
		f=1.0
		if maxWidth:
			if w>maxWidth:
				f=maxWidth*1.0/w
				
		if maxHeight:
			if h>maxHeight:
				f=min(f, maxHeight*1.0/h)
		
		resolution*=f
		w*=f
		h*=f
		
		t=transform.Transform()
		t.scale(resolution/72.0, resolution/72.0)
		t.rotate(angle)
		x0, y0, x1, y1=t.applyRect((x0, y0, x1, y1))
		t.translate(-x0, -y0)
		t.translate(xDelta, yDelta)
		
		self.renderPage(name, t, int(w), int(h), aaLevel=aaLevel, colorSpace=colorSpace)
		
	def renderPage(self, name, t, width, height, aaLevel=-1, colorSpace="DeviceGray"):
		
		transform1=Matrix(a=t.a, b=t.b, c=t.c, d=t.d, e=t.e, f=t.f)
		bbox=BBox(x0=0, y0=0, x1=width, y1=height)
		
		if aaLevel!=-1:
			self.dll.fz_set_aa_level(self.context, aaLevel)
			
		fz_device_rgb=self.dll.fz_find_device_colorspace(self.context, colorSpace)
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