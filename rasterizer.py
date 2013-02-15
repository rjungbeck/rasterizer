import os
import multiprocessing
import sys

import converter
import mupdf
		
if __name__=="__main__":
	if "--multiprocessing-fork" in sys.argv:
		sys.argv=[sys.executable, "--multiprocessing-fork", sys.argv[sys.argv.index("--multiprocessing-fork")+1]]
		multiprocessing.freeze_support()
	mupdf.main()