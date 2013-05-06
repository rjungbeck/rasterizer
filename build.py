import argparse
import subprocess
import json
import sys
import shutil
import os

def pythonCall(command, cwd=None):
	subprocess.call(command, shell=True)
	
def pythonRelCall(relCommand, command, cwd=None):
	pythonPath=os.path.dirname(sys.executable)
	fullPath=os.path.join(pythonPath, relCommand)
	pythonCall(fullPath + " " + command, cwd=cwd)

def main():
	parser=argparse.ArgumentParser(description="Rasterizer Builder", epilog="(C) Copyright 2013 by RSJ Software GmbH Germering. All rights reserved.")
	parms=parser.parse_args()
		
	with open("version.json", "r") as f:
		version=json.load(f)
		
	versionPart=version.split(".")
	
	version="%d.%02d.%04d" %(int(versionPart[0]), int(versionPart[1]), int(versionPart[2])+1)
	
	print "Building", version
	
	with open("version.json", "w") as f:
		json.dump(version, f)
	
	#Empty Distribution
	shutil.rmtree("dist", True)
	shutil.rmtree("build", True)
	shutil.rmtree("Output", True)
	
	# Py2Exe
	pythonCall("setup.py")
	
	# Inno Setup
	subprocess.call(r'"c:\Program Files (x86)\Inno Setup 5\iscc.exe" -dversion=' + version + ' rasterizer.iss')
	
if __name__=="__main__":
	main()
