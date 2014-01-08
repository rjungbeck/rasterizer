import argparse
import json
import multiprocessing
import os
import logging

import win32api
import win32service
import win32serviceutil

cmdline_style="pywin32"

logger=logging.getLogger("servicebase")

class ServiceBase(win32serviceutil.ServiceFramework):
	_svc_name_ = "RsjService"
	_svc_display_name_ = "RSJ Service"
	_svc_deps_=[]
	epilog="(C) Copyright 2013-2014 by RSJ Software GmbH Germering. All rights reserved."
	options={}
	
	def __init__(self, args=None):
		if args:
			#self._svc_name_=args[0]
			try:
				win32serviceutil.ServiceFramework.__init__(self, args)
			except:
				pass
					
	def SvcDoRun(self):
		import servicemanager
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
		
		directory=self.getOption("directory")

		if directory:
			os.chdir(directory)
		
		self.ServiceRun()
		
		servicemanager.LogInfoMsg("%s - STOPPED!" %(self._svc_display_name_,))
	
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.ServiceStop()

	def ServiceMain(self):
		
		multiprocessing.freeze_support()
		win32api.SetConsoleCtrlHandler(self.ctrlHandler, True)
	
		parser=argparse.ArgumentParser(self._svc_display_name_, epilog=self.epilog, fromfile_prefix_chars="@")
		
		customInstallOptions=""
		for k,v in self.options.iteritems():
			customInstallOptions+=k[1:]+":"
			parser.add_argument(k, type=str, default=v.get("default", None),help=v.get("help", None))
		
		parser.add_argument("--username", type=str, default=None, help="User name")
		parser.add_argument("--password", type=str, default=None, help="Password")
		parser.add_argument("--startup", type=str, default="manual", help="Startup type (auto, manual, disabled)")
		
		subparsers=parser.add_subparsers(help="Subcommands")
		
		parserInstall=subparsers.add_parser("install", help="Install Service")
		
		parserUninstall=subparsers.add_parser("remove", help="Remove Service")
		
		parserConfig=subparsers.add_parser("update", help="Update Service")
		
		parserDebug=subparsers.add_parser("debug", help="Debug")
		
		parserStart=subparsers.add_parser("start", help="Start Service")
		
		parserStop=subparsers.add_parser("stop", help="Stop Service")
		
		parserRestart=subparsers.add_parser("restart", help="Restart Service")
		
		self.__name__=self.__class__.__name__
			
		win32serviceutil.HandleCommandLine(self,customInstallOptions=customInstallOptions, customOptionHandler=self.customOptionHandler)
			
	def ServiceRun(self):
		pass
		
	def ServiceStop(self):
		pass
		
	def ctrlHandler(self, ctrlType):
		return True
		
	def customOptionHandler(self, opts):
		logger.debug(opts)
	
		for opt,val in opts:
			if opt in self.options:
				if "name" in self.options[opt]:
					self.setOption(self.options[opt]["name"], val) 
			
		self.setOption("directory", os.getcwd()) 
		
	def setOption(self, name, val):
		win32serviceutil.SetServiceCustomOption(self, name, val)
		
	def getOption(self, name, default=None):
		return win32serviceutil.GetServiceCustomOption(self, name, default)
