import sys

from mupdf11 import MuPdf as MuPdf11
from mupdf12 import MuPdf as MuPdf12

class MuPdf(object):
	def __new__(cls, *args, **kw):
		if sys.getwindowsversion().major>5:
			ret=MuPdf12(*args, **kw)
		else:
			ret=MuPdf11(*args, **kw)
		return ret
