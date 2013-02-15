import multiprocessing
import os
import os.path
import sys

import mupdf

def Produce(target,conn):
	try:
		# instDir=os.path.dirname(sys.executable)
		# os.chdir(instDir)
		mupdf.pipeMain(conn)
	except KeyboardInterrupt:
		pass
		
class Converter():
	def __init__(self,target):
		self.parentPipe, self.childPipe=multiprocessing.Pipe()
		self.process=multiprocessing.Process(target=Produce, args=[target, self.childPipe])
		self.process.start()
		
	def convert(self, **parms):
		command=""
		for k in parms:
			command+=" --"+k+" " +str(parms[k])
			
		self.parentPipe.send(command)
		return self.parentPipe.recv()