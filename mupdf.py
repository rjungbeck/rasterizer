import sys

from mupdfold import MuPdf as MuPdfOld
from mupdfnew import MuPdf as MuPdfNew

class MuPdf(object):
	def __new__(cls, *args, **kw):
		if sys.getwindowsversion().major>5:
			ret=MuPdfNew(*args, **kw)
		else:
			ret=MuPdfOld(*args, **kw)
		return ret
		