#!/usr/bin/env python3
#FOCAS TEST
import socket,time
from struct import pack,unpack

#HOST = '192.168.0.70'
HOST = '192.168.0.61'
PORT = 8193

FRAME_SRC=b'\x00\x01';FRAME_DST=b'\x00\x02';FRAMEHEAD=b'\xa0\xa0\xa0\xa0'
FRAME_OPEN=b'\x01\x01';FRAME_OPEN_OK=b'\x01\x02'
FRAME_CLOSE=b'\x02\x01';FRAME_CLOSE_OK=b'\x02\x02'
FRAME_VAR=b'\x21\x01';FRAME_VAR_OK=b'\x21\x02'

class focas():
	def __init__(self, ip, port=8193):
		self.sock=None
		self.ip=ip
		self.port=port
		self.connected=False
	def connect(self):
		try:
			self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((HOST, PORT))
			self.sock.settimeout(1)
			self.sock.sendall(self.encap(FRAME_OPEN,FRAME_DST,0))
			data=self.decap(self.sock.recv(1500),0)
			if data["cmd"]==FRAME_OPEN_OK:
				self.connected=True
			self.getsysinfo()
		except:
			print("ERROR")
			self.sock=None
			self.connected=False
	def disconnect(self):
		if self.connected:
			self.sock.sendall(self.encap(FRAME_CLOSE,FRAME_DST,0))
			data=self.sock.recv(1024)
	def encap(self,command,payload,type=1):
		r=pack(">H",len(payload)+(2 if type==1 else 0))+payload
		if type==1: r=pack(">H",len(r)+2)+FRAME_SRC+r
		return FRAMEHEAD+FRAME_SRC+command+r
	def decap(self,data,type=1):
		if len(data)<10: return {"len":-1}
		if not data.startswith(b'\xa0'*4): return {"len":-1}
		src,cmd,len1=data[4:6],data[6:8],unpack(">H",data[8:10])[0]
		if len1+10 != len(data): return {"len":-1}
		if len1==0: return {"len":0,"cmd":cmd,"src":src,"data":b'0'}
		data=data[10:]
		if type==0: return {"len":len1,"cmd":cmd,"src":src,"data":data[10:]}
		if len(data)<4: return {"len":-1}
		src2,len1=data[2:4],unpack(">H",data[2:4])[0]
		if len1+2 != len(data): return {"len":-1}
		if len1<2: return {"len":0,"cmd":cmd,"src":src,"data":b'0'}
		else: return {"len":len1-2,"cmd":cmd,"src":src,"data":data[4:]}
	def getsysinfo(self):
		self.sock.sendall(self.encap(FRAME_VAR,b'\x00\x01\x00\x01\x00\x18'+b'\x00'*20,1))
		t=self.decap(self.sock.recv(1500))
		self.sysinfo=None
		if t["len"]==0: return None
		elif t["cmd"]!=FRAME_VAR_OK: return None
		if t["data"].startswith(b'\x00\x01\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x12'):
			self.sysinfo={}
			self.sysinfo['addinfo'],self.sysinfo['maxaxis']=unpack(">HH",t["data"][-18:-14])
			self.sysinfo['cnctype'],self.sysinfo['mttype']=t["data"][-14:-12],t["data"][-12:-10]
			self.sysinfo['series'],self.sysinfo['version'],self.sysinfo['axes']=t["data"][-10:-6],t["data"][-6:-2],t["data"][-2:]
	def readparam(first,count,axis):
		#a0 a0 a0 a0 00 01 21 01 00 1e 00 01 00 1c 00 01 00 01 00 0e 00 00 03 e8 00 00 03 fc ff ff ff ff 00 00 00 00 00 00 00 00
		pass
	def readaxis():
		# READ ABS a0 a0 a0 a0 00 01 21 01 00 1e 00 01 00 1c 00 01 00 01 00 26 00 00 00 04 ff ff ff ff 00 00 00 00 00 00 00 00 00 00 00 00
		# READ REL a0 a0 a0 a0 00 01 21 01 00 1e 00 01 00 1c 00 01 00 01 00 26 00 00 00 06 ff ff ff ff 00 00 00 00 00 00 00 00 00 00 00 00
		# READ REF a0 a0 a0 a0 00 01 21 01 00 1e 00 01 00 1c 00 01 00 01 00 26 00 00 00 01 ff ff ff ff 00 00 00 00 00 00 00 00 00 00 00 00

		# a0 a0 a0 a0 00 02 21 02 00 52 00 01 00 50 00 01 00 01 00 26 00 00 00 00 00 00 00 40
		# 00 05 7e b8 00 0a 00 04
		# 00 0a 2d 66 00 0a 00 04
		# ff fe cc 80 00 0a 00 04
		# 00 01 2b 7b 00 0a 00 04
		# ff df 17 88 00 0a 00 04
		# 00 00 75 30 00 0a 00 04
		# 00 00 00 00 00 0a 00 04
		# 00 00 00 00 00 0a 00 04
		pass
	def readdiag(self,axis,first,last=0):
		if last==0:last=first
		self.sock.sendall(self.encap(FRAME_VAR,b'\x00\x01\x00\x01\x00\x30'+pack(">IIiII",first,last,axis,0,0),1))
		t=self.decap(self.sock.recv(1500))
		r={}
		if t["len"]==0: return None
		elif t["cmd"]!=FRAME_VAR_OK: return None
		if t["data"].startswith(b'\x00\x01\x00\x01\x00\x30\x00\x00\x00\x00\x00\x00'):
			numbers=unpack(">H",t["data"][12:14])[0]//(self.sysinfo["maxaxis"]*4+8)
			for x in range(numbers):
				pos=14+x*(self.sysinfo["maxaxis"]*4+8)
				varname,axiscount,valtype=unpack(">IhH",t["data"][pos:pos+8])
				values={"type":valtype,"axis":axiscount,"data":[]}
				for n in range(self.sysinfo["maxaxis"]):
					value=t["data"][pos+8+4*n:pos+8+4*(n+1)]
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
		if last==0:last=first
		self.sock.sendall(self.encap(FRAME_VAR,b'\x00\x01\x00\x01\x00\x15'+pack(">IIIII",first,last,0,0,0),1))
		t=self.decap(self.sock.recv(1500))
		r={}
		if t["len"]==0: return None
		elif t["cmd"]!=FRAME_VAR_OK: return None
		if t["data"].startswith(b'\x00\x01\x00\x01\x00\x15\x00\x00\x00\x00\x00\x00'):
			for x in range(unpack(">H",t["data"][12:14])[0]//8):
				pos=14+8*x
				val=t["data"][pos:pos+8]
				if val[-3:-2]==b'\x02':
					if val[-2:]==b'\xff\xff': r[first+x]=None
					else: r[first+x]=unpack(">i",val[0:4])[0]/2**val[7]
				else:
					r[first+x]=val
		return r
	def readpmc(self,datatype,section,first,count=1):
		if datatype>0 and datatype<4:
			last=first+(1<<datatype)*count-1
			self.sock.sendall(self.encap(FRAME_VAR,b'\x00\x02\x00\x01\x80\x01'+pack(">IIII",first,last,section,datatype)+b'\x00'*4,1))
			t=self.decap(self.sock.recv(1500))
			r={}
			if t["len"]==0: return None
			elif t["cmd"]!=FRAME_VAR_OK: return None
			if t["data"].startswith(b'\x00\x02\x00\x01\x80\x01\x00\x00\x00\x00\x00\x00'):
				for x in range(unpack(">H",t["data"][12:14])[0]>>datatype):
					pos=14+(1<<datatype)*x
					if datatype==0: value=t["data"][pos]
					elif datatype==1: value=unpack(">H",t["data"][pos:pos+2])[0]
					elif datatype==2: value=unpack(">I",t["data"][pos:pos+4])[0]
					r[first+(1<<datatype)*x]=value
			return r
		return None

# D1870 remain-wirelength in m
# D1874 wirelength complete
# D2204 conductivity*48

if __name__ == "__main__":
	conn=focas(HOST,PORT)
	conn.connect()
	if conn.connected:
		print("open ok 2")
		n=conn.readpmc(1,9,2204,1)
		if n is not None:
			print("Leitwert %0.1f" % (n[2204]/48))
		n=conn.readpmc(2,9,1870,2)
		if n is not None:
			print("Laenge: %i von %i (%0.1f %%)" % (n[1870],n[1874],n[1870]/n[1874]*100))
		n=conn.readdiag(-1,308,309)
		print(n)
	conn.disconnect()