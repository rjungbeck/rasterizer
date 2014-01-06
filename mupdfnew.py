from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER

class Matrix(Structure):
	_fields_=[("a", c_float),("b", c_float),("c", c_float),("d", c_float),("e", c_float),("f", c_float)]

class Rect(Structure):
	_fields_=[("x0", c_float), ("y0", c_float), ("x1", c_float), ("y1", c_float)]
	
class BBox(Structure):
	_fields_=[("x0", c_int), ("y0", c_int), ("x1", c_int), ("y1", c_int)]
	
FZ_STORE_UNLIMITED=0
	
class MuPdf():
	def __init__(self):
		self.dll=cdll.libmupdf
		self.dll.fz_scale.argtypes=[POINTER(Matrix), c_float, c_float]
		self.dll.fz_scale.restype=POINTER(Matrix)
		
		self.dll.fz_rotate.argtypes=[POINTER(Matrix), c_float]
		self.dll.fz_rotate.restype=POINTER(Matrix)
		
		self.dll.fz_translate.argtypes=[POINTER(Matrix), c_float, c_float]
		self.dll.fz_translate.restype=POINTER(Matrix)
		
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
		
		self.dll.fz_write_pam.argtypes=[c_void_p, c_void_p, c_char_p, c_int]
		self.dll.fz_write_pam.restype=None
		
		self.dll.fz_write_pbm.argtypes=[c_void_p, c_void_p, c_char_p]
		self.dll.fz_write_pbm.restype=None
		
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
		
		#self.doc=self.dll.fz_open_document(self.context, name)
		
	def getPageCount(self):
		return self.dll.fz_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.fz_load_page(self.doc, num-1)
		
	def render(self,name,angle=0,resolution=300.0, xDelta=0.0, yDelta=0.0, aaLevel=-1,maxWidth=0, maxHeight=0, colorSpace="DeviceGray"):
		if aaLevel!=-1:
			self.dll.fz_set_aa_level(self.context, aaLevel)
			
		rect=Rect()
		self.dll.fz_bound_page(self.doc, self.page,rect)
		
		w=abs(rect.x0-rect.x1)*resolution/72.0
		h=abs(rect.y0-rect.y1)*resolution/72.0
		if angle==90 or angle==270:
			w,h=h,w
			
		f=1.0
		if maxWidth:
			if w>maxWidth:
				f=maxWidth*1.0/w
				
		if maxHeight:
			if h>maxHeight:
				f=min(f, maxHeight*1.0/h)
		
		resolution*=f
		
		transform=Matrix()
		self.dll.fz_scale(transform, resolution/72.0, resolution/72.0)
		transform1=Matrix()
		transform2=Matrix()
		self.dll.fz_rotate(transform2, angle)
		self.dll.fz_concat(transform1, transform, transform2) 
		transform3=Matrix()
		self.dll.fz_translate(transform3, xDelta, yDelta)
		self.dll.fz_concat(transform2, transform1, transform3)
		
		self.dll.fz_transform_rect(rect, transform2)
		bbox=BBox()
		self.dll.fz_round_rect(bbox,rect)
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