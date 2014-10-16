import argparse
import os
import tempfile

import win32print
import win32ui

from PIL import Image,ImageWin

from mupdf import MuPdf

LOGPIXELSX=88
LOGPIXELSY=90
PLANES=14
HORZRES=8
VERTRES=10

def DoPrint(parms):
	printProducer=PrintProducer()
	
	if parms.printer==None:
		parms.printer=win32print.GetDefaultPrinter()
	
	if parms.docName==None:
		parms.docName=parms.inPdf
		
	printProducer.printPdf(parms.printer, parms.inPdf, docName=parms.docName, prnFile=parms.prnFile)
	
class PrintProducer(object):
	
	def openPrinter(self, printerName):
		self.hDC=win32ui.CreateDC()
		self.hDC.CreatePrinterDC(printerName)
		
	def getPrintableArea(self):
		printableArea=self.hDC.GetDeviceCaps(HORZRES), self.hDC.GetDeviceCaps(VERTRES)
		return printableArea
		
	def getPlanes(self):
		planes=self.hDC.GetDeviceCaps(PLANES)
		return planes
		
	def getResolution(self):
		resolution=self.hDC.GetDeviceCaps(LOGPIXELSX), self.hDC.GetDeviceCaps(LOGPIXELSY)
		return resolution
		
	def closePrinter(self):
		self.hDC.DeleteDC()
		self.hDC=None
		
	def  printPdf(self, printer, pdfName, prnFile=None, docName=""):
		self.openPrinter(printer)
		
		colorspace="DeviceRGB"
		
		resolutionX,resolutionY=self.getResolution()
		printableArea=self.getPrintableArea()
			
		self.muPdf=MuPdf()
		with open(pdfName, "rb") as pdfFile:
			self.muPdf.load(pdfFile.read())
			count=self.muPdf.getPageCount()
			
			self.hDC.StartDoc(docName, prnFile)
			
			for i in range(1, count+1):
				self.muPdf.loadPage(i)
				
				pageSize=self.muPdf.getSize()
				
				angle=0
				
				if pageSize[2]>pageSize[3]:
					if printableArea[0]<printableArea[1]:
						angle=90
				else:
					if printableArea[0]>printableArea[1]:
						angle=90
						
				handle,pngName=tempfile.mkstemp(suffix=".png")
				os.fdopen(handle).close()				
				self.muPdf.render(pngName, angle, resolutionX,colorSpace=colorspace, maxWidth=printableArea[0], maxHeight=printableArea[1])
				self.muPdf.freePage()
				
				with open(pngName, "rb") as pngFile:
					bmp=Image.open(pngFile)
				
					x,y=bmp.size
				
					self.hDC.StartPage()
					dib=ImageWin.Dib(bmp)
					dib.draw(self.hDC.GetHandleOutput(), (0,0,x,y))
					self.hDC.EndPage()
				
					bmp=None
				os.unlink(pngName)
				
			self.hDC.EndDoc()
				
			self.closePrinter()
			
def main():
	parser=argparse.ArgumentParser(description="PDF Printer", epilog="(C) Copyright 2014 by RSJ Software GmbH Germering. All rights reserved.")
	parser.add_argument("--printer", type=str, default=win32print.GetDefaultPrinter(), help="Printer name")
	parser.add_argument("pdf", type=str, help="PDF File")
	parms=parser.parse_args()
	
	pp=PrintProducer()
	pp.printPdf(parms.printer, parms.pdf)
	
if __name__=="__main__":
	main()
	