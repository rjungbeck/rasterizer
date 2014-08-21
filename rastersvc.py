import sys 

import servicebase
from serve import serve,stop

cmdline_style="pywin32"

class RasterizerService(servicebase.ServiceBase):
	_svc_name_ = "RasterizerService"
	_svc_display_name_ = "Rasterizer"
	_svc_deps_=["tcpip"]
	options={"-c": {"default": "rastersvc.json", "name":"config", "help":"Config File"}}
	
	def  ServiceRun(self):
		self.port=int(self.getOption("port", default="8000"))
		self.configPath=self.getOption("config", default="conf/rastersvc.json")
		serve(self)

	def ServiceStop(self):
		stop()

def HandleCommandLine():
	main()
	
def main():
	RasterizerService(sys.argv).ServiceMain()
	
if __name__=="__main__":
	main()
