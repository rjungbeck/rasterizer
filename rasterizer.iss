
[Setup]
AppId="Rasterizer"
AppName="RSJ PDF Rasterizer"
AppVerName=RSJ Rasterizer {#version}
AppPublisher=RSJ Software GmbH
AppPublisherURL=http://www.rsj.de
AppSupportURL=http://www.rsj.de
AppUpdatesURL=http://www.rsj.de
DefaultDirName={pf32}\\rasterizer
DefaultGroupName=RSJ Rasterizer
OutputBaseFilename=RasterizerInst
Compression=lzma
SolidCompression=yes
InternalCompressLevel=ultra
VersionInfoCompany=RSJ Software GmbH
VersionInfoCopyright=Copyright (C) 2013 by RSJ Software GmbH Germering. All rights reserved.
VersionInfoDescription=RSJ Rasterizer Installer
VersionInfoProductName="Rasterizer"
VersionInfoVersion={#version}
VersionInfoProductVersion={#version}
VersionInfoTextVersion={#version}
VersionInfoProductTextVersion={#version}
ArchitecturesInstallIn64BitMode=x64 ia64
ShowLanguageDialog=no
WizardImageStretch=no
MinVersion=0,5.01.2600sp2

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: COPYING;

[Files]
Source: dist\*; DestDir: {app};  Flags: ignoreversion overwritereadonly uninsrestartdelete recursesubdirs;
Source: version.json; DestDir: {app}; Flags: ignoreversion overwritereadonly uninsrestartdelete;

Source: *.py; DestDir: {app}\src;  Flags: ignoreversion overwritereadonly uninsrestartdelete; 
Source: *.iss; DestDir: {app}\src;  Flags: ignoreversion overwritereadonly uninsrestartdelete; 
Source: mupdf\*; DestDir: {app}\src\mupdf;  Flags: ignoreversion overwritereadonly uninsrestartdelete recursesubdirs; 


[Run]

[Registry]

[UninstallRun]

