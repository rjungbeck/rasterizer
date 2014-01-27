from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER

import transform

class Matrix(Structure):
	_fields_=[("a", c_float),("b", c_float),("c", c_float),("d", c_float),("e", c_float),("f", c_float)]

class Rect(Structure):
	_fields_=[("x0", c_float), ("y0", c_float), ("x1", c_float), ("y1", c_float)]

class BBox(Structure):
	_fields_=[("x0", c_int), ("y0", c_int), ("x1", c_int), ("y1", c_int)]

class MuPdfBase(object):

	def __init__(self):

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

		self.setContext()

	def open(self, name):
		with open(name, "rb") as f:
			self.content=f.read()
			self.load(self.content)

	def load(self, content):
		self.content=content
		if self.context==None:
			self.context=self.setContext()

		self.stream=self.dll.fz_open_memory(self.context, self.content, len(self.content))
		self.loadDocument(self.context,  self.stream)

	def render(self,name,angle=0,resolution=300.0, xDelta=0.0, yDelta=0.0, aaLevel=-1,maxWidth=0, maxHeight=0, colorSpace="DeviceGray", x0=0.0, y0=0.0, x1=0.0, y1=0.0):
		if x0==0.0 and y0==0.0 and x1==0.0 and y1==0.0:
			x0,y0,x1,y1=self.getSize()
		
		#Determine size
		t=transform.Transform()
		t.scale(resolution/72.0, resolution/72.0)
		t.rotate(angle)
		
		nx0, ny0, nx1, ny1 = t.applyRect((x0,y0,x1, y1))
		
		# Scale
		if maxWidth or maxHeight:
			f=1.0
			if maxWidth:
				if nx1-nx0> maxWidth:
					f=maxWidth/(nx1-nx0)

			if maxHeight:
				if ny1-ny0>maxHeight:
					f=min(maxHeight/(ny1-ny0), f)
				
			t.scale(f, f)
			
			nx0, ny0, nx1, ny1 = t.applyRect((x0,y0,x1, y1))
		
		# Determine position
		t2=transform.Transform()
		t2.translate(-nx0, -ny0)
		t2.transform(t)
		t=t2
		
		# Shift
		if xDelta or yDelta:
			t.translate(-xDelta, -yDelta)
			
		#self.renderPage(name, t, bbox, aaLevel=aaLevel, colorSpace=colorSpace)
		self.renderPage(name, t, (int(nx1-nx0), int(ny1-ny0)), aaLevel=aaLevel, colorSpace=colorSpace)

	def renderPage(self, name, t, size, aaLevel=-1, colorSpace="DeviceGray"):

		transform1=Matrix(a=t.a, b=t.b, c=t.c, d=t.d, e=t.e, f=t.f)
		bbox=BBox(x0=0, y0=0, x1=size[0], y1=size[1])

		if aaLevel!=-1:
			self.dll.fz_set_aa_level(self.context, aaLevel)

		fz_device_rgb=self.findColorspace(colorSpace)
		pix=self.dll.fz_new_pixmap_with_bbox(self.context, fz_device_rgb, bbox)
		self.dll.fz_clear_pixmap_with_value(self.context, pix, 255)
		dev=self.dll.fz_new_draw_device(self.context, pix)
		self.runPage(dev, transform1)
		self.dll.fz_free_device(dev)
		dev=None
		self.dll.fz_write_png(self.context, pix, name, 0)
		self.dll.fz_drop_pixmap(self.context, pix)
		pix=None

	def close(self):
		if self.stream:
			self.dll.fz_close(self.stream)
			self.stream=None

		self.closeDocument()

		if self.doc:
			self.dll.fz_close_document(self.doc)
			self.doc=None

	def freeContext(self):
		if self.context:
			self.dll.fz_free_context(self.context)
			self.context=None