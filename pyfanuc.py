#!/usr/bin/env python3
#0.1 pyfanuc init release
#0.11 extend to multipacket
#0.12 readaxis
import socket,time,datetime
from struct import pack,unpack

class pyfanuc(object):
	def __init__(self, ip, port=8193):
		self.sock=None
		self.ip=ip
		self.port=port
		self.connected=False
	FTYPE_OPN_REQU=0x0101;FTYPE_OPN_RESP=0x0102
	FTYPE_VAR_REQU=0x2101;FTYPE_VAR_RESP=0x2102
	FTYPE_CLS_REQU=0x0201;FTYPE_CLS_RESP=0x0202
	FRAME_SRC=b'\x00\x01'
	FRAME_DST=b'\x00\x02';FRAME_DST2=b'\x00\x01'
	FRAMEHEAD=b'\xa0\xa0\xa0\xa0'
	def connect(self):
		"Establish connection to machine and set parameters with sysinfo"
#		try:
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(5)
		self.sock.connect((self.ip,self.port))
		self.sock.settimeout(1)
		self.sock.sendall(self._encap(pyfanuc.FTYPE_OPN_REQU,pyfanuc.FRAME_DST))
		data=self._decap(self.sock.recv(1500))
		if data["ftype"]==pyfanuc.FTYPE_OPN_RESP:
			self.connected=True
		self.getsysinfo()
#		except:
#		print("ERROR")
#		self.sock=None
#		self.connected=False
		return self.connected
	def disconnect(self):
		"Disconnect the connection to the machine"
		if self.connected:
			self.sock.sendall(self._encap(pyfanuc.FTYPE_CLS_REQU,b''))
			data=self._decap(self.sock.recv(1500))
			if data["ftype"]==pyfanuc.FTYPE_CLS_RESP:
				return True
		return False

	def _encap(self,ftype,payload,fvers=1):
		"intern function - Encapsulate packetdata"
		if ftype==pyfanuc.FTYPE_VAR_REQU:
			pre=[]
			if isinstance(payload,list):
				for t in payload:
					pre.append(pack(">H",len(t)+2)+t)
				payload=pack(">H",len(pre))+b''.join(pre)
			else:
				payload=pack(">HH",1,len(payload)+2)+payload
		return pyfanuc.FRAMEHEAD+pack(">HHH",fvers,ftype,len(payload))+payload
	def _decap(self,data):
		"intern function - Decapsulate packetdata"
		if len(data)<10:
			return {"len":-1}
		if not data.startswith(b'\xa0'*4):
			return {"len":-1}
		fvers,ftype,len1=unpack(">HHH",data[4:10])
		if len1+10 != len(data):
			return {"len":-1}
		if len1==0:
			return {"len":0,"ftype":ftype,"fvers":fvers,"data":b'0'}
		data=data[10:]
		if ftype==pyfanuc.FTYPE_VAR_RESP:
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
	def _req_rdsingle(self,c1,c2,c3,v1=0,v2=0,v3=0,v4=0,v5=0,pl=b""):
		"intern function - pack simple command"
		cmd=pack(">HHH",c1,c2,c3)
		self.sock.sendall(self._encap(pyfanuc.FTYPE_VAR_REQU,cmd+pack(">iiiii",v1,v2,v3,v4,v5)+pl))
		t=self._decap(self.sock.recv(1500))
		if t["len"]==0:
			return {"len":-1}
		elif t["ftype"]!=pyfanuc.FTYPE_VAR_RESP:
			return {"len":-1}
		elif t["data"][0].startswith(cmd+b'\x00'*6):
			return {"len":unpack(">H",t["data"][0][12:14])[0],"data":t["data"][0][14:]}
		elif t["data"][0].startswith(cmd):
			return {"len":0,"data":t["data"][0][6:],"error":unpack(">h",t["data"][0][6:8])[0]}
		else:
			return {"len":-1}
	def _req_rdmulti(self,l):
		"intern function - pack multiple commands"
		self.sock.sendall(self._encap(pyfanuc.FTYPE_VAR_REQU,l))
		t=self._decap(self.sock.recv(1500))
		if t["len"]==0:
			return {"len":-1}
		elif t["ftype"]!=pyfanuc.FTYPE_VAR_RESP:
			return {"len":-1}
		if len(l) != len(t["data"]):
			return {"len":-1}
		for x in range(len(t["data"])):
			if t["data"][x][0:6] == l[x][0:6]:
				if t["data"][x][6:12]==b'\x00'*6:
					t["data"][x]=[0,t["data"][x][12:]]
				else:
					t["data"][x]=[unpack('>h',t["data"][x][0:2])[0],t["data"][x][12:]]
			else:
				return {"len":-1}
		return t
	def _req_rdsub(self,c1,c2,c3,v1=0,v2=0,v3=0,v4=0,v5=0):
		"intern function - pack subfunction info"
		return pack(">HHHiiiii",c1,c2,c3,v1,v2,v3,v4,v5)
	def _decode8(self,val):
		"intern function - decode value from 8 bytes"
		if val[5]==2 or val[5]==10:
			if val[-2:]==b'\xff'*2:
				return None
			else:
				return unpack(">i",val[0:4])[0]/val[5]**val[7]
	def statinfo(self):
		"""
		Get state of machine
		"""
		st=self._req_rdsingle(1,1,0x19,0)
		if (self.sysinfo["cnctype"]==b"16" or self.sysinfo["cnctype"]==b"31") and st["len"]==0xe:
			return dict(zip(['aut','run','motion','mstb','emegency','alarm','edit'],
			unpack(">HHHHHHH",st["data"])))
	def getdate(self):
		"""
		Get date
		returns [YEAR,MONTH,DAY]
		"""
		st=self._req_rdsingle(1,1,0x45,0)
		if st["len"]==0xc:
			return unpack(">HHH",st["data"][0:6])
	def gettime(self):
		"""
		Get time
		returns [HOUR,MINUTE,SECOND]
		"""
		st=self._req_rdsingle(1,1,0x45,1)
		if st["len"]==0xc:
			return unpack(">HHH",st["data"][-6:])
	def getdatetime(self):
		"""
		Get date and time
		returns time.struct_time
		"""
		st=self._req_rdmulti([self._req_rdsub(1,1,0x45,0),self._req_rdsub(1,1,0x45,1)])
		if st["len"]<0:
			return
		if len(st["data"]) != 2:
			return
		if st["data"][0][0]!=0 or st["data"][1][0]!=0:
			return
		if unpack(">H",st["data"][0][1][0:2])[0] == 0xc and unpack(">H",st["data"][1][1][0:2])[0] == 0xc:
			return datetime.datetime(*unpack(">HHHHHH",st["data"][0][1][2:8]+st["data"][1][1][-6:])).timetuple()
	def getsysinfo(self):
		"""
		Get sysinfo
		returns ['addinfo','maxaxis','cnctype','mttype','series','version','axes']
		"""
		st=self._req_rdsingle(1,1,0x18)
		if st["len"]==0x12:
			self.sysinfo=dict(zip(['addinfo','maxaxis','cnctype','mttype','series','version','axes'],
			unpack(">HH2s2s4s4s2s",st["data"])))

	ABS=1;REL=2;REF=4;SKIP=8;DIST=16
	ALLAXIS=-1
	def readaxes(self,what=1,axis=ALLAXIS):
		r=[]
		axvalues=(("ABS",pyfanuc.ABS,4),("REL",pyfanuc.REL,6),("REF",pyfanuc.REF,1),("SKIP",pyfanuc.SKIP,8),("DIST",pyfanuc.DIST,7))
		for u,v,w in axvalues:
			if what & v:
				r.append(self._req_rdsub(1,1,0x26,w,axis))
		st=self._req_rdmulti(r)
		if st["len"]<0:
			return
		r={}
		for x in st["data"]:
			ret1=[]
			if x[0]!=0:
				ret1=None
			else:
				for pos in range(2,unpack(">H",x[1][0:2])[0]+2,8):
					value=x[1][pos:pos+8]
					ret1.append(self._decode8(value))
			for u,v,w in axvalues:
				if what & v:
					r[u]=ret1
					what &= ~v
					break
		return r
	def readparam(self,axis,first,last=0):
		if last==0:last=first
		st=self._req_rdsingle(1,1,0x0e,first,last,axis)
		if st["len"]<0:
			return
		r={}
		for pos in range(0,st["len"],self.sysinfo["maxaxis"]*4+8):
			varname,axiscount,valtype=unpack(">IhH",st["data"][pos:pos+8])
			values={"type":valtype,"axis":axiscount,"data":[]}
			for n in range(pos+8,pos+self.sysinfo["maxaxis"]*4+8,4):
				value=st["data"][n:n+4]
				if valtype==0:
					value=value[-1] #bit 1bit / Byte
				elif valtype==1:
					value=[(value[-1] >> n)& 1 for n in range(7,-1,-1)] #bit 8bit
				elif valtype==2:
					value=unpack(">h",value[-2])[0] #short
				elif valtype==3:
					value=unpack(">i",value)[0] #int
				if axiscount != -1:
					values["data"].append(value)
					break
				else:
					values["data"].append(value)
			r[varname]=values
		return r
	def readdiag(self,axis,first,last=0):
		if last==0:last=first
		st=self._req_rdsingle(1,1,0x30,first,last,axis)
		if st["len"]<0:
			return
		r={}
		for pos in range(0,st["len"],self.sysinfo["maxaxis"]*4+8):
			varname,axiscount,valtype=unpack(">IhH",st["data"][pos:pos+8])
			values={"type":valtype,"axis":axiscount,"data":[]}
			for n in range(pos+8,pos+self.sysinfo["maxaxis"]*4+8,4):
				value=st["data"][n:n+4]
				if valtype==4 or valtype==0:
					value=value[-1] #bit 1bit / Byte
				elif valtype==1:
					value=unpack(">h",value[-2])[0] #short
				elif valtype==2:
					value=unpack(">i",value)[0] #int
				elif valtype==3:
					value=[(value[-1] >> n)& 1 for n in range(7,-1,-1)] #bit 8bit
				if axiscount != -1:
					values["data"].append(value)
					break
				else:
					values["data"].append(value)
			r[varname]=values
		return r
	def readmacro(self,first,last=0):
		if last==0: last=first
		st=self._req_rdsingle(1,1,0x15,first,last)
		if st["len"]<=0:
			return
		r={}
		for pos in range(0,st["len"],8):
			r[first]=self._decode8(st["data"][pos:pos+8])
			first+=1
		return r
	def readpmc(self,datatype,section,first,count=1):
		last=first+(1<<datatype)*count-1
		st=self._req_rdsingle(2,1,0x8001,first,last,section,datatype)
		if st["len"]<=0:
			return
		r={}
		for x in range(st["len"]>>datatype):
			pos=(1<<datatype)*x
			if datatype==0:
				value=st["data"][pos]
			elif datatype==1:
				value=unpack(">H",st["data"][pos:pos+2])[0]
			elif datatype==2:
				value=unpack(">I",st["data"][pos:pos+4])[0]
			r[first+(1<<datatype)*x]=value
		return r
	def readexecprog(self,chars=256):
		st=self._req_rdsingle(1,1,0x20,chars)
		if st["len"]<=4:
			return
		return {"block":unpack(">i",st["data"][0:4])[0],"text":st["data"][4:].decode()}
	def readprognum(self):
		"""
		Get the running program and main program numbers
		returns [running,main]
		"""
		st=self._req_rdsingle(1,1,0x1c)
		if st["len"]<8:
			return
		return {"run":unpack(">i",st["data"][0:4])[0],"main":unpack(">i",st["data"][4:])[0]}
	def settime(self,h=-1,m=0,s=0):
		"""
		Set Time to Parameter-Values or actual PC-Time
		variant 1 - requests nothing for actual PC-Time to set
		variant 2 - requests hour,optional minute (default 0),optional second (default 0)
		"""
		if h==-1:
			t=time.localtime()
			h,m,s=t.tm_hour,t.tm_min,t.tm_sec
		self.sock.sendall(self._encap(pyfanuc.FTYPE_VAR_REQU,self._req_rdsub(1,1,0x46,1,0,0,0,12)+b'\x00'*6+pack(">HHH",h,m,s)))
		t=self._decap(self.sock.recv(1500))
		if t["len"]==18:
			if t["ftype"]==pyfanuc.FTYPE_VAR_RESP and unpack(">HHH",t["data"][0][0:6])==(1,1,0x46):
				return unpack(">h",t["data"][0][6:8])[0]
	def listprog(self,start=1):
		ret={}
		while True:
			st=self._req_rdsingle(1,1,0x06,start,0x13,2)
			if st["len"] < -1:
				return None
			elif st["len"]==0:
				return ret
			for t in range(0,st["len"],72):
				number,size,comment=unpack(">II64s",st["data"][t:t+72])
				comment=comment.split(b'\0', 1)[0]
				start=number+1
				ret[number]={"size":size,"comment":comment.decode()}
	def readalarm(self):
		"Read alarm Bitfield"
		st=self._req_rdsingle(1,1,0x1a)
		if st["len"]==4:
			return unpack(">L",st["data"])[0]
		return None
	def readalarmcode(self,type,withtext=0,maxmsgs=-1,textlength=32):
		"Read alarm code / msg"
		#readalarmmsg	Returns Alarmcode+Msgtext	1,1,0x23,int32 Type,int32 MaxMsgs,int32 0 w/o or 1/2 with text,int32 MaxTextLength
		#											int32 AlarmCode,int32 AlarmType,int32 Axis,int32 TextLength,text/trash
		if maxmsgs<=0:
			maxmsgs=int(self.sysinfo['axes'])
		st=self._req_rdsingle(1,1,0x23,type,maxmsgs,withtext,textlength)
		ret=[]
		if st["len"] > 0:
			for pos in range(0,st["len"],4*4+textlength):
				entry=dict(zip(['alarmcode','alarmtype','axis'],unpack(">iii",st["data"][pos:pos+4*3])))
				txlen=unpack(">i",st["data"][pos+4*3:pos+4*4])[0]
				if txlen>0 and withtext>0:
					entry["text"]=st["data"][pos+4*4:pos+4*4+textlength]
				ret.append(entry)
			return ret
		return None
	def readdir_current(self,fgbg=1): #31i
		"""
		Get current directory
		requests 1 (default) for foreground or 2 for background
		returns directoryname
		"""
		st=self._req_rdsingle(1,1,0xb0,fgbg)
		if st["len"]>=0:
			p=st["data"].split(b'\0', 1)[0]
			return p.decode()
		return None
	def readdir_info(self,dir): #31i
		buffer=bytearray(0x100)
		bdir=dir.encode()
		buffer[0:len(bdir)]=bdir
		st=self._req_rdsingle(1,1,0xb4,0,0,0,0,256,buffer)
		if st["len"]>=8:
			return dict(zip(['dirs','files'],unpack(">ii",st["data"])))
		return None
	def readdir(self,dir,first=0,count=10,type=0,size=1): #30i
		buffer=bytearray(0x100)
		bdir=dir.encode()
		buffer[0:len(bdir)]=bdir
		st=self._req_rdsingle(1,1,0xb3,first,count,type,size,256,buffer)
		x=[]
		if st["len"]>=8:
			for t in range(0,st["len"],128):
				n=dict(zip(['type','datetime','unkn','size','attr','name','comment','proctimestamp'],unpack(">h12s6sII36s52s12s",st["data"][t:t+128])))
				del n['unkn']
				if n['type']==1:
					n['comment']=n['comment'].split(b'\0', 1)[0].decode()
					n['datetime']=datetime.datetime(*unpack(">HHHHHH",n['datetime'])).timetuple()
				else:
					n['comment']=None
					n['size']=None
					n['datetime']=None
				n['name']=n['name'].split(b'\0', 1)[0].decode()
				n['type']='D' if n['type']==0 else 'F'
				x.append(n)
			return(x)
		return None
	def readdir_complete(self,dir): #30i
		t=self.readdir_info(dir)
		n=t['dirs']+t['files']
		ret=[]
		for t in range(0,n,10):
			x=self.readdir(dir,first=t,count=10)
			if not x is None:
				ret.extend(x)
			else:
				break
		return ret
	def getprog(self,name): #TEST Stream
		"""
		Get program-file
		requests filename
		returns filecontent
		"""
		q=b''
		if isinstance(name,int):
			q=("O%04i-O%04i" % (name,name)).encode()
		elif isinstance(name,str):
			name=name.upper()
			if not name.startswith("O"):
				name="O"+name
			if name.find("-")==-1:
				name=name+"-"+name
			q=name.encode()
		else:
			return -1
		buffer=bytearray(0x204)
		self.sock2=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock2.connect((self.ip,self.port))
		self.sock2.settimeout(1)
		self.sock2.sendall(self._encap(pyfanuc.FTYPE_OPN_REQU,pyfanuc.FRAME_DST2))
		data=self._decap(self.sock2.recv(1500))
		buffer[0:4]=b'\x00\x00\x00\x01'
		buffer[4:4+len(q)]=q #buffer[4:15]=b'\x4f\x30\x31\x30\x30\x2d\x4f\x30\x31\x30\x30'
		self.sock2.sendall(self._encap(0x1501,buffer))
		data=self._decap(self.sock2.recv(1500))
		#print(data)
		f=b''
		n=b''
		while True:
			n+=self.sock2.recv(1500)
			while len(n)>=10:
				if n[:4]==pyfanuc.FRAMEHEAD:
					fvers,ftype,flen=unpack(">HHH",n[4:10])
					if len(n)<flen:
						break
					n=n[10:]
					if ftype==0x1604: #a0 a0 a0 a0 00 02 16 04 05 00
						f+=n[:flen]
						n=n[flen:]
					elif ftype==0x1701: #a0 a0 a0 a0 00 02 17 01 00 00
						self.sock2.sendall(self._encap(0x1702,b'')) #a0 a0 a0 a0 00 01 17 02 00 00
						return f.decode()
				else:
					return -1
		return -1
	def readactfeed(self):
		"""
		Get actual feedrate
		returns feedrate
		"""
		st=self._req_rdsingle(1,1,0x24)
		return self._decode8(st['data']) if st['len']==8 else None
	def readactspindlespeed(self):
		"""
		Get actual spindlespeed
		returns spindlespeed
		"""
		st=self._req_rdsingle(1,1,0x25)
		return self._decode8(st['data']) if st['len']==8 else None

# D1870 remain-wirelength in m
# D1874 wirelength complete
# D2204 conductivity*48

import locale
locale.setlocale(locale.LC_ALL, 'deu_deu')
if __name__ == '__main__':
	conn=pyfanuc('192.168.0.70')
	if conn.connect():
		print("connected")
#		for t in conn.readdir_complete("//CNC_MEM/USER/PATH1/"):
#			print(t)
#		for n in conn.readdir_complete("//CNC_MEM/USER/PATH1/"):
#			print(n['name']+" ("+time.strftime("%c",n['datetime'])+')' if n['type']=='F' else '<'+n['name']+'>')
		print(conn.getdatetime())
		#print(conn.readaxes(pyfanuc.ABS | pyfanuc.DIST))
		#print(conn._req_rdsingle(1,1,0x8a))
	if conn.disconnect():
		print("disconnected")

#	conn=pyfanuc('192.168.0.61')
#	if conn.connect():
#		print("connected")
#		print(conn.sysinfo)
#		print(conn.readactfeed())
#	if conn.disconnect():
#		print("disconnected")
