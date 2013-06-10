# Rasterizer

## Features 

* Rasterize PDF files (page by page) into PNG files.
* Convert PNG file into printer specific PRN file with Windows printer driver.
* Convert PNG into PCX or RLL file
* Command line and pipe interface

## Command Line
    rasterizer --help

    rasterizer convert [<option>]... <pdf> <pngPrefix> 
        --help
        --angle <angle>
        --resolution <resolution>
        --xdelta <xdelta>
        --ydelta <ydelta>
        --aalevel <aalevel>
	--prnPrefix <prnPrefix>
	--pcxPrefix <pcxPrefix>
	--rllPrefix <rllPrefix>
	--printer <printerName>

    rasterizer pipe
        --help
        --angle <angle>
        --resolution <resolution>
        --xdelta <xdelta>
        --ydelta <ydelta>
        --aalevel <aalevel>
        --printer <printer>
        --page <page>
        --pngPrefix <pngPrefix>
        --prnPrefix <prnPrefix>
        --tmpPrefix <tmpPrefix>
	--pcxPrefix <pcxPrefix>
	--rllPrefix <rllPrefix>
        --keep <keep>
	
## Technology
Python program using ctypes for interfacing with mupdf library and Windows GDI.

        
