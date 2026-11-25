import struct


BUMPPROTO = 1
HUMPPROTO = 2;
CHUMPPROTO= 3;

THEPROTO = HUMPPROTO;

REQop = 1;
DATAop= 2;
ACKop = 3;
ERRORop=4;
HANDOFFop=5;

SERVERPORT = 4715;
SAMEPORT   = 4716;

INITTIMEOUT = 2.5;   # **seconds**
SHORTSIZE = 2;            # in bytes
INTSIZE   = 4;
BASESIZE  = 2;
MAXDATASIZE=512;
DHEADERSIZE = BASESIZE + SHORTSIZE + INTSIZE; 	# DATA header size
EHEADERSIZE = BASESIZE + SHORTSIZE;
MAXSIZE  = DHEADERSIZE + MAXDATASIZE;

EBADPORT  =1;  # packet from wrong port */
EBADPROTO =2;  # unknown protocol */
EBADOPCODE=3;  # unknown opcode */
ENOFILE   =4;  # REQ for nonexistent file */
ENOPERM   =5;  # REQ for file with wrong permissions */

def protocol(buf): return buf[0]

def opcode(buf): return buf[1]

class BASE:
    proto = 0		# byte
    opcode = 0		# byte
    
    def __init__(self, proto, opcode):
        self.proto = proto
        self.opcode= opcode
        
    # def __init__(self, buf):
    
    def size(self): 
        return BASESIZE
        
    def proto(self): 
        return self.proto
    
    def opcode(self): 
        return self.opcode
        
# end of class BASE


class REQ (BASE):

    winsize = 0		# int16
    filename = ''	# null-terminated string
    
    '''
    def __init__(self, proto, winsize, filename):
        super(self, proto, wumppkt.REQop)
        self.winsize = winsize
        self.filename= filename
    ''' 
    def __init__(self, winsize, filename):
        super().__init__(HUMPPROTO, REQop)
        self.winsize = winsize
        self.filename= filename
    
    # __init__(self, bbuf):		# not needed
    
    def write(self):	# returns a byte array representing the packet body
        # bbuf = bytearray()
        # bbuf.append(self.proto)
        # bbuf.append(self.opcode)
        fnlen = len(self.filename)
        fmt = '>BBH{}sB'.format(fnlen)
        bbuf = struct.pack(fmt, self.proto, self.opcode, self.winsize, self.filename.encode('ascii'), 0)
        # print('REQ.write filename', self.filename, '   bbuf:', bbuf)
        return bbuf
        
    
    def size(self):
        return super.size() + SHORTSIZE + len(self.filename) + 1
    
    def filename(self):
        return self.filename()
        
# end of REQ class


class HANDOFF (BASE):	

    _newport = 0
    
    def __init__(self):
        super().__init__(HUMPPROTO, REQop)
        _newport = 0
        

    @staticmethod
    def read(buf):			# build a handoff packet from an incoming buffer. 
        (proto, opcode, newport) = struct.unpack('>BBH', buf)
        h = HANDOFF()
        h.proto = proto
        h.opcode = opcode
        h._newport = newport
        # print('newport is', newport)
        return h
    
    def newport(self):
        return self._newport
        
# end of class HANDOFF


class ACK (BASE):

    blocknum = 0
    
    def __init__(self, blocknum):
        super().__init__(THEPROTO, ACKop)
        self.blocknum = blocknum
        
    def write(self):	# returns a byte array representing the packet body
        bbuf = struct.pack('>BBHI', self.proto, self.opcode, 0, self.blocknum)
        return bbuf
        
    def size(self):
        return super.size() + SHORTSIZE + INTSIZE
        
# end of class ACK


class DATA(BASE):

    _blocknum = 0
    databuf = b''
    
    # construct packet from blocknum and buf; not used
    def __init__(self, blocknum, databuf):
        super().__init__(THEPROTO, DATAop)
        self._blocknum = blocknum
        self.databuf = databuf
        
    @staticmethod
    def read(buf):      # RETURNS a DATA object read from the buffer. Really a static method.
        # d = DATA()
        datalen = len(buf) - BASESIZE - SHORTSIZE - INTSIZE
        fmt = '>BBHI{}s'.format(datalen)
        (proto, opcode, zero, blocknum, databuf) = struct.unpack(fmt, buf)
        d = DATA(blocknum, databuf)
        return d        
        
    def blocknum(self):
        return self._blocknum

# end of class DATA














