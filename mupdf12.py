from mupdfbase import MuPdfBase, Matrix, Rect, BBox
from ctypes import cdll,c_float, c_int, c_void_p, Structure, c_char_p,POINTER
	
class MuPdf(MuPdfBase):
	
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
		
		self.dll.fz_write_pam.argtypes=[c_void_p, c_void_p, c_char_p, c_int]
		self.dll.fz_write_pam.restype=None
		
		self.dll.fz_write_pbm.argtypes=[c_void_p, c_void_p, c_char_p]
		self.dll.fz_write_pbm.restype=None
		
		MuPdfBase.__init__(self)
		
	def getSize(self):
		rect=Rect()
		self.dll.fz_bound_page(self.doc, self.page,rect)
		return rect.x0, rect.y0, rect.x1, rect.y1
	
	