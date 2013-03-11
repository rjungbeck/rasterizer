from distutils.core import setup
import py2exe


setup(name="PDF-Rasterizer",
	version="1.00.0000",
	description="Convert PDF into PNG and PRN",
	author="Ruediger Jungbeck, RSJ Software GmbH",
	author_email="ruediger.jungbeck@rsj.de",
	url="http://www.rsj.de",
	console=["rasterizer.py"],
	data_files=[("",["COPYING", "libmupdf.dll", r"dll\mfc90.dll", r"dll\mfc90u.dll", r"dll\mfcm90.dll", r"dll\mfcm90u.dll", r"dll\Microsoft.VC90.MFC.manifest"])],
	zipfile="rasterizer.zip",
	options = {"py2exe": { "includes": [], 
		 "dll_excludes": [ "mswsock.dll", "powrprof.dll",'w9xpopen.exe' ],
		"optimize":2,
		"bundle_files":3,
		"compressed":True}
		},
		)

