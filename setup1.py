import sys
from cx_Freeze import setup, Executable

build_exe_options= {"optimize":2, "include_msvcr":True, "include_files":[("COPYING", "COPYING"),("libmupdf.dll", "libmupdf.dll")], "bin_excludes":["mswsock.dll", "powrprof.dll"]}
bdist_msi_options={"upgrade_code":"{5304FD3F-EAFC-4829-945F-0CAB73948CA3}"}

data_files=[("",["COPYING", "libmupdf.dll", r"dll\mfc90.dll", r"dll\mfc90u.dll", r"dll\mfcm90.dll", r"dll\mfcm90u.dll", r"dll\Microsoft.VC90.MFC.manifest"])]


setup(name="PDF-Rasterizer",
	version="1.00.0000",
	description="Convert PDF into PNG and PRN",
	author="Ruediger Jungbeck, RSJ Software GmbH",
	author_email="ruediger.jungbeck@rsj.de",
	url="http://www.rsj.de",
	data_files=data_files,
	options = {"build_exe": build_exe_options,
		"bdist_msi": bdist_msi_options}, 
	executables=[Executable(script="rasterizer.py",compress=True,appendScriptToLibrary=True, targetName="rasterizer.exe")]		
	)

