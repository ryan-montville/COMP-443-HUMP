from wumppkt import *
from socket import *
import sys
import time

def main():
    srcport = 0
    destport = SERVERPORT
    filename = 'vanilla'
    desthost = 'ulam.cs.luc.edu'
    winsize  = 1
    latchport = 0
    expected_block = 1
    
    args = sys.argv
    
    if len(args) > 1: filename = args[1]
    if len(args) > 2: winsize = int(args[2])
    if len(args) > 3: desthost = args[3]
    if len(args) > 4: print('usage: wclient.py filename [winsize [hostname]]')
    
    print('Looking up address of {}... '.format(desthost), file=sys.stderr, end='')
    try:
        dest = gethostbyname(desthost)
    except (GAIerror, herror) as mesg:     # GAIerror: error in gethostbyname()
        errno,errstr=mesg.args
        print("\n   ", errstr, file=sys.stderr);
        return;
    print("got it: " + dest, file=sys.stderr)
    addr=(dest, destport)                  # a socket address
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(INITTIMEOUT)             
    
    # build REQ and send it
    
    req = REQ(winsize, filename)
    reqbody = req.write()
    # print('reqbody:', reqbody, file=sys.stderr)
    s.sendto(reqbody, (dest, destport))
    
    ##########################################################
    # wait for handoff, send ACK[0]
    
    try:
        (buf, src) = s.recvfrom(1024)
    except TimeoutError:
        print('hard timeout waiting for HANDOFF', file=sys.stderr)
        return
    
    # print('length of buf received: ', len(buf), file=sys.stderr)
    # print(buf, file=sys.stderr)
    h = HANDOFF()
    h = h.read(buf)
    newport = h.newport()
    print('HANDOFF received; new port is', newport, file=sys.stderr)
    
    # send ACK[0] to newport
    # What do you have to do to create and send ACK[0]? See below where ACK[n] is sent
    ack = ACK(0)
    ackbody = ack.write()
    s.sendto(ackbody, (dest, newport))
    
    ##########################################################
    # main loop: wait for each DATA[N] and send ACK[N] in response
    # all DATA[N] must come from newport
    
    while True:
    
       try:
           (buf, src) = s.recvfrom(1024)
       except TimeoutError:
           print('timeout', file=sys.stderr)
           return
       except:
           return
       
       # proto = protocol(buf)
       # OPcode = opcode(buf)
       srcport = src[1]
       
       if protocol(buf) == THEPROTO and opcode(buf) == DATAop and len(buf) >= DHEADERSIZE:
           data = DATA(0, '').read(buf)		# this is ugly
           
       printinfo(buf, src)
       
       #print(data)
       # print('blocknum: ', data.blocknum())
       block = data.blocknum()
       print('received block', block, file=sys.stderr)
       
       if expected_block == block:
            sys.stdout.buffer.write(data.databuf)
       ack = ACK(expected_block)		# pld: something will need to be fixed here for later blocks
       s.sendto(ack.write(), (dest, newport))
       if expected_block == block:
                   expected_block += 1
       if len(data.databuf) < MAXDATASIZE: return

#################################################################       
# prints packet type, length, protocol, source, etc
# pktbuf is the entire packet body, including the HUMP header

def printinfo(pktbuf, pktsrc):
    pkt_proto = protocol(pktbuf)
    pkt_opcode = opcode(pktbuf)
    length = len(pktbuf)
    print('received packet: length={}, proto={}, opcode={}, source=({},{}), time={}'.format(
    	length, pkt_proto, pkt_opcode, pktsrc[0], pktsrc[1], time.time_ns() // 1000000), file=sys.stderr)
    if pkt_opcode == DATAop:
        data = DATA.read(pktbuf)		# python static method from class DATA
        print('    DATA packet, block={}'.format(data.blocknum()), file=sys.stderr)
    

main()
