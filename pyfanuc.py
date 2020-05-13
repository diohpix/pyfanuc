#!/usr/bin/env python3
#FOCAS TEST 0.1 begin
#0.11 extend to multipacket
import socket,time
from struct import pack,unpack

HOST = '192.168.0.70'
#HOST = '192.168.0.61'
PORT = 8193

class focas():
	def __init__(self, ip, port=8193):
		self.sock=None
		self.ip=ip
		self.port=port
		self.connected=False
		self.FTYPE_OPN_REQU=0x0101;self.FTYPE_OPN_RESP=0x0102
		self.FTYPE_VAR_REQU=0x2101;self.FTYPE_VAR_RESP=0x2102
		self.FTYPE_CLS_REQU=0x0201;self.FTYPE_CLS_RESP=0x0202
		self.FRAME_SRC=b'\x00\x01';self.FRAME_DST=b'\x00\x02';self.FRAMEHEAD=b'\xa0\xa0\xa0\xa0'
	def connect(self):
#		try:
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((HOST, PORT))
		self.sock.settimeout(1)
		self.sock.sendall(self.encap(self.FTYPE_OPN_REQU,self.FRAME_DST))
		data=self.decap(self.sock.recv(1500))
		if data["ftype"]==self.FTYPE_OPN_RESP:
			self.connected=True
		self.getsysinfo()
#		except:
		# print("ERROR")
		# self.sock=None
		# self.connected=False
		return self.connected
	def disconnect(self):
		if self.connected:
			self.sock.sendall(self.encap(self.FTYPE_CLS_REQU,b''))
			data=self.decap(self.sock.recv(1500))
			if data["ftype"]==self.FTYPE_CLS_RESP: return True
		return False
	def encap(self,ftype,payload,fvers=1):
		if ftype==self.FTYPE_VAR_REQU:
			pre=[]
			if isinstance(payload,list):
				for t in payload: pre.append(pack(">H",len(t)+2)+t)
				payload=pack(">H",len(pre))+b''.join(pre)
			else:
				payload=pack(">HH",1,len(payload)+2)+payload
		return self.FRAMEHEAD+pack(">HHH",fvers,ftype,len(payload))+payload
	def decap(self,data):
		if len(data)<10: return {"len":-1}
		if not data.startswith(b'\xa0'*4): return {"len":-1}
		fvers,ftype,len1=unpack(">HHH",data[4:10])
		if len1+10 != len(data): return {"len":-1}
		if len1==0: return {"len":0,"ftype":ftype,"fvers":fvers,"data":b'0'}
		data=data[10:]
		if ftype==self.FTYPE_VAR_RESP:
			re=[]
			qu=unpack(">H",data[0:2])[0]
			n=2
			for t in range(qu):
				le=unpack(">H",data[n:n+2])[0]
				re.append(data[n+2:n+le])
				n+=le
			return {"len":len1,"ftype":ftype,"fvers":fvers,"data":re}
		else: # ftype==FTYPE_OPN_RESP or ftype==FTYPE_CLS_RESP
			return {"len":len1,"ftype":ftype,"fvers":fvers,"data":data}
	def _req_single(self,c1,c2,c3,v1=0,v2=0,v3=0,v4=0,v5=0):
		cmd=pack(">HHH",c1,c2,c3)
		self.sock.sendall(self.encap(self.FTYPE_VAR_REQU,cmd+pack(">iiiii",v1,v2,v3,v4,v5)))
		t=self.decap(self.sock.recv(1500))
		if t["len"]==0: return {"len":-1}
		elif t["ftype"]!=self.FTYPE_VAR_RESP: return {"len":-1}
		elif t["data"][0].startswith(cmd+b'\x00'*6): return {"len":unpack(">H",t["data"][0][12:14])[0],"data":t["data"][0][14:]}
		else: return {"len":-1}
	def getsysinfo(self):
		st=self._req_single(1,1,0x18)
		if st["len"]==0x12:
			st=st["data"]
			self.sysinfo={'cnctype':st[4:6],'mttype':st[6:8],'series':st[8:12],'version':st[12:16],'axes':st[16:]}
			self.sysinfo['addinfo'],self.sysinfo['maxaxis']=unpack(">HH",st[0:4])
	def readparam(self,axis,first,last=0):
		cmd=pack(">HHH",1,1,0xe)
		if last==0:last=first
		self.sock.sendall(self.encap(self.FTYPE_VAR_REQU,cmd+pack(">IIiII",first,last,axis,0,0)))
		t=self.decap(self.sock.recv(1500))
		r={}
		if t["len"]==0: return None
		elif t["ftype"]!=self.FTYPE_VAR_RESP: return None
		st=t["data"][0]
		if st.startswith(cmd+b'\x00'*6):
			numbers=unpack(">H",st[12:14])[0]//(self.sysinfo["maxaxis"]*4+8)
			for x in range(numbers):
				pos=14+x*(self.sysinfo["maxaxis"]*4+8)
				varname,axiscount,valtype=unpack(">IhH",st[pos:pos+8])
				values={"type":valtype,"axis":axiscount,"data":[]}
				for n in range(self.sysinfo["maxaxis"]):
					value=t["data"][0][pos+8+4*n:pos+8+4*(n+1)]
					if valtype==0: value=value[-1] #bit 1bit / Byte
					elif valtype==1: value=[(value[-1] >> n)& 1 for n in range(7,-1,-1)] #bit 8bit
					elif valtype==2: value=unpack(">h",value[-2])[0] #short
					elif valtype==3: value=unpack(">i",value)[0] #int
					if axiscount != -1:
						values["data"].append(value)
						break
					else:
						values["data"].append(value)
				r[varname]=values
		return r
	def readaxis():
		pass
	def readdiag(self,axis,first,last=0):
		cmd=pack(">HHH",1,1,0x30)
		if last==0:last=first
		self.sock.sendall(self.encap(self.FTYPE_VAR_REQU,cmd+pack(">IIiII",first,last,axis,0,0)))
		t=self.decap(self.sock.recv(1500))
		r={}
		if t["len"]==0: return None
		elif t["ftype"]!=self.FTYPE_VAR_RESP: return None
		st=t["data"][0]
		if st.startswith(cmd+b'\x00'*6):
			numbers=unpack(">H",st[12:14])[0]//(self.sysinfo["maxaxis"]*4+8)
			for x in range(numbers):
				pos=14+x*(self.sysinfo["maxaxis"]*4+8)
				varname,axiscount,valtype=unpack(">IhH",st[pos:pos+8])
				values={"type":valtype,"axis":axiscount,"data":[]}
				for n in range(self.sysinfo["maxaxis"]):
					value=t["data"][0][pos+8+4*n:pos+8+4*(n+1)]
					if valtype==4 or valtype==0: value=value[-1] #bit 1bit / Byte
					elif valtype==1: value=unpack(">h",value[-2])[0] #short
					elif valtype==2: value=unpack(">i",value)[0] #int
					elif valtype==3: value=[(value[-1] >> n)& 1 for n in range(7,-1,-1)] #bit 8bit
					if axiscount != -1:
						values["data"].append(value)
						break
					else:
						values["data"].append(value)
				r[varname]=values
		return r
	def readmacro(self,first,last=0):
		cmd=pack(">HHH",1,1,0x15)
		if last==0: last=first
		self.sock.sendall(self.encap(self.FTYPE_VAR_REQU,cmd+pack(">IIIII",first,last,0,0,0)))
		t=self.decap(self.sock.recv(1500))
		r={}
		if t["len"]==0: return None
		elif t["ftype"]!=self.FTYPE_VAR_RESP: return None
		st=t["data"][0]
		if st.startswith(cmd+b'\x00'*6):
			for x in range(unpack(">H",st[12:14])[0]//8):
				pos=14+8*x
				val=t["data"][0][pos:pos+8]
				if val[-3:-2]==b'\x02':
					if val[-2:]==b'\xff\xff': r[first+x]=None
					else: r[first+x]=unpack(">i",val[0:4])[0]/2**val[7]
				else:
					r[first+x]=val
		return r
	def readpmc(self,datatype,section,first,count=1):
		last=first+(1<<datatype)*count-1
		st=self._req_single(2,1,0x8001,first,last,section,datatype)
		if st["len"]<=0:return
		r={}
		for x in range(st["len"]>>datatype):
			pos=(1<<datatype)*x
			if datatype==0: value=st["data"][pos]
			elif datatype==1: value=unpack(">H",st["data"][pos:pos+2])[0]
			elif datatype==2: value=unpack(">I",st["data"][pos:pos+4])[0]
			r[first+(1<<datatype)*x]=value
		return r

# D1870 remain-wirelength in m
# D1874 wirelength complete
# D2204 conductivity*48

conn=focas(HOST,PORT)
if conn.connect():
	print("connected")
#	print(conn.sysinfo)
	n=conn.readpmc(1,9,2204,1)
	print(n)
#	if n is not None:
#		print("Leitwert %0.1f" % (n[2204]/48))
#	n=conn.readpmc(2,9,1870,2)
#	if n is not None:
#		print("Laenge: %i von %i (%0.1f %%)" % (n[1870],n[1874],n[1870]/n[1874]*100))
#	n=conn.readdiag(-1,308,309)
#	print(n)
#	n=conn.readparam(-1,1240,1250)
#	print(n)
if conn.disconnect():print("disconnected")
