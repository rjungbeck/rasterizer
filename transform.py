from math import sin,cos,tan,pi,radians
    
class Transform(object):
	def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
		self.a=a
		self.b=b
		self.c=c
		self.d=d
		self.e=e
		self.f=f 
		
	def tostring(self):
		return "%f,%f,%f,%f,%f,%f" %(self.a,self.b,self.c,self.d,self.e,self.f)
	
	def fromstring(self, string):
		wrk=string.split(",")
		self.a=float(wrk[0])
		self.b=float(wrk[1])
		self.c=float(wrk[2])
		self.d=float(wrk[3])
		self.e=float(wrk[4])
		self.f=float(wrk[5])
		return self
		
	def transform(self, other):
		self.a,self.b,self.c,self.d,self.e,self.f=(self.a*other.a+self.c*other.b, self.b*other.a+self.d*other.b, self.a*other.c+self.c*other.d, self.b*other.c+self.d*other.d, self.a*other.e+self.c*other.f+self.e, self.b*other.e+self.d*other.f+self.f)		
		return self
		
	def transformDir(self, a,b,c,d,e,f):
		self.a,self.b,self.c,self.d,self.e,self.f=(self.a*a+self.c*b, self.b*a+self.d*b, self.a*c+self.c*d, self.b*c+self.d*d, self.a*e+self.c*f+self.e, self.b*e+self.d*f+self.f)		
		return self		
		
	def translate(self, dx, dy):
		self.e+=self.a*dx+self.c*dy
		self.f+=self.b*dx+self.d*dy				
		return self
		
	def scale(self,x,y):
		self.a*=x
		self.b*=x
		self.c*=y 
		self.d*=y
		return self
		
	def rotate(self, theta):
		a=radians(theta)
		c=cos(a)
		s=sin(a)
		
		self.a,self.b,self.c,self.d=(self.a*c+self.c*s, self.b*c+self.d*s, -self.a*s+self.c*c, -self.b*s+self.d*c )				
		return self
		
	def skew(self, alpha, beta):
		tanAlpha=tan(radians(alpha))
		tanBeta=tan(radians(beta))
		
		self.a,self.b,self.c,self.d=(self.a*10.0+self.c*tanAlpha, self.b*10.0+self.d*tanAlpha, self.a*tanBeta+self.c, self.b*tanBeta+self.d)		
		return self
		
	def det(self):
		return self.a*self.d-self.c*self.b
		
	def inverse(self):
		d=self.det()
		self.a,self.b,self.c,self.d,self.e,self.f=(self.d/d, -self.b /d, -self.c/d, self.a/d,  (self.c*self.f-self.d*self.e)/d, (self.b*self.e-self.a*self.f)/d)
		return self
		
	def isEqual(self, other):
		eta=1e-6
		if abs(self.a-other.a) >eta or abs(self.b-other.b)>eta or abs(self.c-other.c)>eta or abs(self.d-other.d)>eta or abs(self.e-other.e)>eta or abs(self.f-other.f)>eta:
			return False
			
		return True
		
	def isLinear(self):
		eta=1e-6
		if abs(self.a-1.0) >eta or abs(self.b)>eta or abs(self.c)>eta or abs(self.d-1.0)>eta:
			return False
			
		return True
		
	def clone(self):
		return Transform(self.a, self.b,self.c,self.d,self.e,self.f)
		
	def apply(self,pos):
		x=self.a*pos[0]+self.c*pos[1]+self.e
		y=self.b*pos[0]+self.d*pos[1]+self.f
		return x,y
		
	def applyRect(self, pos):
		nx0,ny0=self.apply((pos[0], pos[1]))
		nx1, ny1=self.apply((pos[0], pos[3]))
		nx2, ny2=self.apply((pos[2], pos[3]))
		nx3, ny3=self.apply((pos[2], pos[1]))
		
		return min(nx0, nx1, nx2, nx3), min(ny0, ny1, ny2, ny3), max(nx0, nx1, nx2, nx3), max(ny0, ny1, ny2, ny3)
		