import argparse

import win32api

def main():
	parser=argparse.ArgumentParser(description="Shell Print",epilog="(C) Copyright 2014 by RSJ Software GmbH Germering. All rights reserved.")
	parser.add_argument("pdf", type=str, help="PDF file")
	parms=parser.parse_args()
	
	win32api.ShellExecute (0, "print", parms.pdf, None, ".", 0)
	
if __name__=="__main__":
	main()

