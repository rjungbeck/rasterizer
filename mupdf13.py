from mupdfbase import MuPdfBase, Matrix, Rect, BBox
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER

FZ_STORE_UNLIMITED=0
	
class MuPdf(MuPdfBase):
	
	def __init__(self):
		self.dll=cdll.libmupdf
		
		self.dll.pdf_bound_page.argtypes=[c_void_p, c_void_p, POINTER(Rect)]
		self.dll.pdf_bound_page.restype=POINTER(Rect)
		
		self.dll.fz_new_pixmap_with_bbox.argtypes=[c_void_p, c_void_p, POINTER(BBox)]
		self.dll.fz_new_pixmap_with_bbox.restype=c_void_p
		
		self.dll.pdf_run_page.argtypes=[c_void_p, c_void_p, c_void_p, POINTER(Matrix), c_void_p]
		self.dll.pdf_run_page.restype=None
		
		self.dll.fz_write_pam.argtypes=[c_void_p, c_void_p, c_char_p, c_int]
		self.dll.fz_write_pam.restype=None
		
		self.dll.fz_write_pbm.argtypes=[c_void_p, c_void_p, c_char_p]
		self.dll.fz_write_pbm.restype=None
		
		self.dll.pdf_count_pages.argtypes=[c_void_p]
		self.dll.pdf_count_pages.restype=c_int
		
		self.dll.pdf_open_document_with_stream.argtypes=[c_void_p, c_void_p]
		self.dll.pdf_open_document_with_stream.restype=c_void_p
		
		self.dll.pdf_close_document.argtypes=[c_void_p]
		self.dll.pdf_close_document.restype=None
		
		self.dll.pdf_free_page.argtypes=[c_void_p, c_void_p]
		self.dll.pdf_free_page.restype=None
		
		self.dll.fz_lookup_device_colorspace.argtypes=[c_void_p, c_char_p]
		self.dll.fz_lookup_device_colorspace.restype=c_void_p
		
		MuPdfBase.__init__(self)
		
	def getSize(self):
		rect=Rect()
		self.dll.pdf_bound_page(self.doc, self.page,rect)
		return rect.x0, rect.y0, rect.x1, rect.y1
		
	def getPageCount(self):
		return self.dll.pdf_count_pages(self.doc)
		
	def loadPage(self, num):
		self.page=self.dll.pdf_load_page(self.doc, num-1)
		
	def runPage(self, dev, transform):
		self.dll.pdf_run_page(self.doc, self.page, dev, transform, None)
		
	def freePage(self):
		self.dll.pdf_free_page(self.doc, self.page)
		self.page=None
		
	def loadDocument(self, context, stream):
		self.doc=self.dll.pdf_open_document_with_stream(self.context, self.stream)
	
	def closeDocument(self):
		if self.doc:
			self.dll.pdf_close_document(self.doc)
			self.doc=None
			
	def findColorspace(self, colorSpace):
		return self.dll.fz_lookup_device_colorspace(self.context, colorSpace)
		
	def setContext(self):
		self.context=self.dll.fz_new_context_imp(None, None, FZ_STORE_UNLIMITED, "1.3")
		
	
		