from distutils.core import setup
import py2exe
import glob
import sys
import json

version=""
	
with open("version.json", "r") as f:
	version=json.load(f)

class Target:
	def __init__(self, **kw):
		self.__dict__.update(kw)
		# for the versioninfo resources
		global version
		self.version = version
		self.company_name = "RSJ Software GmbH"
		self.copyright = "(C) Copyright 2013-2014 by RSJ Software GmbH Germering. All rights reserved."
		self.name = "Rasterizer"

if len(sys.argv)==1:
	sys.argv.append("py2exe")
	sys.argv.append("-q")

data_files=[("",["COPYING", "libmupdf.dll", "libmupdf22.dll", r"dll\mfc90.dll", r"dll\mfc90u.dll", r"dll\mfcm90.dll", r"dll\mfcm90u.dll", r"dll\Microsoft.VC90.MFC.manifest"]),
	("Microsoft.VC90.CRT", glob.glob("Microsoft.VC90.CRT/*")),
	("fonts", glob.glob("fonts/*"))]

sys.path.append("Microsoft.VC90.CRT")

rasterSvc = Target(description = 'Raster Service', modules = ['rastersvc'], cmdline_style='custom', dest_base="RasterSvc")
rasterizer=Target(description="Rasterizer", script="rasterizer.py", dest_base="Rasterizer")

setup(name="PDF-Rasterizer",
	version=version,
	description="Convert PDF into PNG and PRN",
	author="Ruediger Jungbeck, RSJ Software GmbH",
	author_email="ruediger.jungbeck@rsj.de",
	url="http://www.rsj.de",
	console=[rasterizer],
	service=[rasterSvc],
	data_files=data_files,
	zipfile="rasterizer.zip",
	options = {"py2exe": { "includes": ["cx_Logging", "win32api"], 
		 "dll_excludes": [ "mswsock.dll", "powrprof.dll",'w9xpopen.exe' ],
		"optimize":2,
		"bundle_files":3,
		"compressed":True}
		},
		)

