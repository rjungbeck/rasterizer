import argparse
import os
import time

import win32print
import win32ui
from PIL import Image
from PIL import ImageWin

def printToFile(imageName, printerName, outName):
	hDC=win32ui.CreateDC()
	hDC.CreatePrinterDC(printerName)
	
	bmp=Image.open(imageName).convert("1")
	x,y=bmp.size
	
	hDC.StartDoc(imageName, outName)
	hDC.StartPage()
	
	dib=ImageWin.Dib(bmp)
	dib.draw(hDC.GetHandleOutput(), (0,0,x,y))
	
	hDC.EndPage()
	hDC.EndDoc()
	hDC.DeleteDC()
	
	for i in range(0, 1000):
		try:
			if os.stat(outName).st_size!=0:
				return True
		except:
			pass
		time.sleep(0.1)
	return False

def main():
	parser=argparse.ArgumentParser(description="Print Image", epilog="(C) Copyright 2013-2014 by RSJ Software GmbH Germering. All rights reserved.")
	parser.add_argument("image", type=str, help="Image file")
	parser.add_argument("printer", type=str, help="Printer name")
	parser.add_argument("out", type=str, help="Output file")
	parms=parser.parse_args()
	
	printToFile(parms.image, parms.printer, parms.out)
	
if __name__=="__main__":
	main()