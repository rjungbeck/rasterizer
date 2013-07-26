import sys

from mupdfold import MuPdf as MuPdfOld
from mupdfnew import MuPdf as MuPdfNew

class MuPdf():
	def __init__(self):
		if sys.getwindowsversion().major>5:
			self.__class__=MuPdfNew
			self.__init__()
		else:
			self.__class__=MuPdfOld
			self.__init__()
		
		