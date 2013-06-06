import argparse
import struct

from PIL import Image

def encode(c):
	return chr(c)

def encodeSigned (c):
	if c<0:
		return chr(256+c)
	return chr(c)

def RllConvert(inName, outName):
	im=Image.open(inName)
	width,height=im.size
	
	pixelData=list(im.getdata())
	
	with open(outName, "wb") as out:
		header=struct.pack(">cBHH","@", 2, width, height)
		out.write(header)
		
		lastLine=None
		lineCopy=0
		maxLineCopy=128
		lastRaw=None
		
		for y in range(height-1, -1, -1):
			lineStart=y*width
		
			thisRaw=pixelData[lineStart:lineStart+width]
			
			if thisRaw!=lastRaw:
				line=list()
				last=255
				count=0
				maxCount=127
				for x in range(width-1, -1, -1):
					#val=im.getpixel((x,y))
					val=pixelData[lineStart+x]
					if val>128:
						val=255
					else:
						val=0
						
					if last==val:
						count+=1
						if count>maxCount:
							line.append(chr(maxCount))
							line.append(chr(0))
							count=1
							maxCount=255
					else:
						line.append(chr(count))
						count=1
						last=val
						maxCount=255
				if count:
					if last==255:
						if count>127:
							line.append(chr(127))
							line.append(chr(0))
							line.append(chr(count-127))
						else:
							line.append(chr(count))
					else:
						line.append(chr(count))
					
				if last!=255:
					line.append(chr(0))
					
				line="".join(line)
				
				if line==lastLine:
					equal=True
				else:
					equal=False
					lastRaw=thisRaw
			else:
				equal=True
			
			if equal:
				lineCopy+=1
				if lineCopy>maxLineCopy:
					out.write(encodeSigned(-maxLineCopy))
					out.write(lastLine)
					out.write(encodeSigned(-maxLineCopy))
					lineCopy=1
			else:
				if lineCopy>1:
					out.write(encodeSigned(-lineCopy))
				if lastLine!=None:
					out.write(lastLine)
				if lineCopy>1:
					out.write(encodeSigned(-lineCopy))
				lineCopy=1
				lastLine=line
		
		if lineCopy>1:
			out.write(encodeSigned(-lineCopy))
		if lastLine!=None:
			out.write(lastLine)
			
		if lineCopy>1:
			out.write(encodeSigned(-lineCopy))

def main():
	parser=argparse.ArgumentParser(description="PRBUF converter", epilog="(C) Copyright 2013 by RSJ Software GmbH Germering. All rights reserved.")
	parser.add_argument("inImage", type=str, help="Input image file")
	parser.add_argument("outFile", type=str, help="Output file")
	parms=parser.parse_args()
	
	RllConvert(parms.inImage, parms.outFile)
		
if __name__=="__main__":
	main()
				
		
	