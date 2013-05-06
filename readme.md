# Rasterizer

## Features 

Rasterize PDF files (page by page) into PNG files.
Convert PNG file into printer specific PRN file with Windows printer driver.
Command line and pipe interface

## Command Line
    rasterizer --help

    rasterizer convert [<option>]... <pdf> <pngPrefix> <printerName> <prnPrefix>
        --help
        --angle <angle>
        --resolution <resolution>
        --xdelta <xdelta>
        --ydelta <ydelta>
        --aalevel <aalevel>

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
        --keep <keep>

        
