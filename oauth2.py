import datetime
import weakref 

import requests
import requests.auth
import requests.adapters 
import requests.models 


class OAuth2(requests.auth.AuthBase):
    def __init__(self, clientId=None, clientSecret=None, authUrl=None, accessToken=None, refreshToken=None, code=None, paramName=None, headerName="Authorization",
                 headerPrefix="Bearer ", redirectUri=None, session=None):
        self.clientId=clientId
        self.clientSecret=clientSecret
        self.authUrl=authUrl
        self.accessToken=accessToken
        self.refreshToken=refreshToken
        self.code=code
        self.paramName=paramName
        self.headerName=headerName
        self.headerPrefix=headerPrefix
        self.redirectUri=redirectUri
        self.expires=None
        
        self.adapter = requests.adapters.HTTPAdapter()

        # Keep a weak reference to the Session, if one is in use.
        # This is to avoid a circular reference.
        self.session = weakref.ref(session) if session else None

        
    def getAccessToken(self):
        now=datetime.datetime.utcnow()
        if self.accessToken:
            if self.expires:
                if now < self.expires:
                    return self.accessToken
                else:
                    self.accessToken=None
            else:
                return self.accessToken
                
        data={"client_id": self.clientId, "client_secret":self.clientSecret}
        
        if self.refreshToken:
            data["refresh_token"]=self.refreshToken
            data["grant_type"]="refresh_token"
        else:
            data["code"]=self.code
            data["redirect_uri"]=self.redirectUri
            data["grant_type"]="authorization_code"
                
        req=requests.post(self.authUrl, data=data)
        if req.status_code==200:
            rsp=req.json()
            self.accessToken=rsp["access_token"]
            self.expires=now+datetime.timedelta(0, rsp["expires_in"])
            if "refresh_token" in rsp:
                self.refreshToken=rsp["refresh_token"]        
        return self.accessToken
        
    def insertAccessToken(self, req):
       self.getAccessToken()
       if self.paramName:
            req.params[self.paramName]=self.accessToken
       elif self.headerName:
            req.headers[self.headerName]=self.headerPrefix+self.accessToken
            
    def retryRequest(self, rsp):
        req=copy_request(rsp.request)
        self.insertAccessToken(req)
        
        if self.pos:
            req.data.seek(self.pos)
       
        adapter = self.adapter
        if self.session:
            session = self.session()
            if session:
                adapter = session.get_adapter(response.request.url)
                
        rsp2=adapter.send(req, **kwArgs)
        return rsp2
        
    def responseHook(self, rsp, **kwArgs):
        if rsp.status_code==403:
            self.accessToken=None
            return self.retryRequest(rsp)
        return rsp
        
    def __call__(self, req):
        self.insertAccessToken(req)
        if self.authUrl and self.clientId and self.clientSecret and self.refreshToken:
            self.pos=None
            try:
                self.pos=req.data.tell()
            except:
                pass
            
            req.register_hook("response", self.responseHook)
        return req
    
def copy_request(request):
    """Copy a Requests PreparedRequest."""
    new_request = requests.models.PreparedRequest()

    new_request.method = request.method
    new_request.url = request.url
    new_request.body = request.body
    new_request.hooks = request.hooks
    new_request.headers = request.headers.copy()

    return new_request