from mupdfbase import MuPdfBase, Matrix, Rect, BBox
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER
	
class MuPdf(MuPdfBase):
	
	def __init__(self):
		self.dll=cdll.libmupdf22
		self.dll.fz_scale.argtypes=[c_float, c_float]
		self.dll.fz_scale.restype=Matrix
		
		self.dll.fz_rotate.argtypes=[c_float]
		self.dll.fz_rotate.restype=Matrix
		
		self.dll.fz_translate.argtypes=[c_float, c_float]
		self.dll.fz_translate.restype=Matrix
		
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
		
		MuPdfBase.__init__(self)
			
	def getSize(self):
		rect=self.dll.fz_bound_page(self.doc, self.page)
		return rect.x0, rect.y0, rect.x1, rect.y1
		
	
		
	
