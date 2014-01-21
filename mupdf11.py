from mupdfbase import MuPdfBase, Matrix, Rect, BBox
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER

FZ_STORE_UNLIMITED=0
	
class MuPdf(MuPdfBase):
	
	def __init__(self):
		self.dll=cdll.libmupdf22
		
		self.dll.fz_bound_page.argtypes=[c_void_p, c_void_p]
		self.dll.fz_bound_page.restype=Rect
	
		self.dll.fz_new_pixmap_with_bbox.argtypes=[c_int, c_int, BBox]
		self.dll.fz_new_pixmap_with_bbox.restype=c_void_p
		
		self.dll.fz_run_page.argtypes=[c_void_p, c_void_p, c_void_p, Matrix, c_void_p]
		self.dll.fz_run_page.restype=None
		
		self.dll.fz_count_pages.argtypes=[c_void_p]
		self.dll.fz_count_pages.restype=c_int
		
		self.dll.fz_open_document_with_stream.argtypes=[c_void_p, c_char_p, c_void_p]
		self.dll.fz_open_document_with_stream.restype=c_void_p
		
		self.dll.fz_close_document.argtypes=[c_void_p]
		self.dll.fz_close_document.restype=None
		
		self.dll.fz_free_page.argtypes=[c_void_p, c_void_p]
		self.dll.fz_free_page.restype=None
		
		self.dll.fz_find_device_colorspace.argtypes=[c_void_p, c_char_p]
		self.dll.fz_find_device_colorspace.restype=c_void_p
		
		MuPdfBase.__init__(self)
			
	def getSize(self):
		rect=self.dll.fz_bound_page(self.doc, self.page)
		return rect.x0, rect.y0, rect.x1, rect.y1
		
	def getPageCount(self):
		return self.dll.fz_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.fz_load_page(self.doc, num-1)
		
	def runPage(self, dev, transform):
		self.dll.fz_run_page(self.doc, self.page, dev, transform, None)
		
	def freePage(self):
		self.dll.fz_free_page(self.doc, self.page)
		self.page=None
		
	def loadDocument(self, context, stream):
		self.doc=self.dll.fz_open_document_with_stream(self.context, "application/pdf", self.stream)
		
	def closeDocument(self):
		if self.doc:
			self.dll.fz_close_document(self.doc)
			self.doc=None
			
	def findColorspace(self, colorSpace):
		return self.dll.fz_find_device_colorspace(self.context, colorSpace)
		
	def setContext(self):
		self.context=self.dll.fz_new_context(None, None, FZ_STORE_UNLIMITED)
		
	
		
	
