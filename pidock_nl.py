import ctypes
import socket
import struct

# import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from libnl.attr import nla_len
from libnl.errno_ import NLE_AGAIN
from libnl.error import errmsg
from libnl.handlers import NL_CB_CUSTOM, NL_CB_SEQ_CHECK, NL_CB_VALID, NL_OK
from libnl.msg import nlmsg_data, nlmsg_hdr, nlmsg_set_default_size
from libnl.nl import nl_recvmsgs_default
from libnl.socket_ import nl_socket_add_memberships, nl_socket_alloc, nl_socket_modify_cb
from libnl.genl.ctrl import genl_ctrl_resolve, genl_ctrl_resolve_grp
from libnl.genl.genl import genl_connect, genlmsg_parse

from event import EventManager

def noop_seq_check(msg, _):
    return NL_OK

class PiDockConnection(object):
    def __init__(self, framebuffer):
        self.framebuffer = framebuffer
        self.sk = nl_socket_alloc()
        sk = self.sk

        # configure callbacks, disable sequence checking
        nl_socket_modify_cb(sk, NL_CB_SEQ_CHECK, NL_CB_CUSTOM, noop_seq_check, None);
        nl_socket_modify_cb(sk, NL_CB_VALID, NL_CB_CUSTOM, self.recvmsg, ctypes.addressof(ctypes.c_void_p.from_buffer(framebuffer)))
        
        rc = genl_connect(sk)
        assert rc==0, 'Failed to connect socket'
        
        family = genl_ctrl_resolve(sk, b'pidock')
        group = genl_ctrl_resolve_grp(sk, b'pidock', b'pidock_mc_group')
        print('family: %d\tgroup: %d' % (family, group))
        
        # Set buffers to handle large payloads
        sk.socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 33554432)
        sk.s_bufsize = 32*4096

        # nl_socket_set_nonblocking(sk)
        sk.socket_instance.setblocking(0)
        nl_socket_add_memberships(sk, group, 0);


    def run_once(self):
        rc = nl_recvmsgs_default(self.sk)
        if rc < 0 and rc != -NLE_AGAIN:
            print('Error: ' + str(rc))

    @staticmethod
    def recvmsg(msg, fb):
        # print('Got Message')
        nlh = nlmsg_hdr(msg)
        tb = [None] * 10

        # TODO: Expect multiple messages from libnl

        rc = genlmsg_parse(nlh, 0, tb, 5, None)
        assert rc == 0, 'genlmsg_parse failed: ' + str(rc)

        x,y,width,height,pitch = struct.unpack('IIIII', tb[2].payload[:nla_len(tb[2])])
        # print('Dirty: (%d, %d)  (%d, %d) %d' % (x,y,width,height, pitch))

        data = tb[3].payload[:nla_len(tb[3])]
        scanline = 1680*4
        offset = scanline * y + x

        assert len(data) >= pitch, '%d %d %d %d %d' % (x,y,width,height,pitch)

        for h in range(height):
            line = pitch*h
            # Using c_void_p type causes segfault!!
            # dst = ctypes.c_void_p.from_address(fb + offset + line)
            # src = ctypes.c_void_p.from_buffer(data[line:])
            dst = fb + offset + scanline * h
            src = ctypes.addressof(ctypes.c_void_p.from_buffer(data[line:]))
            ctypes.memmove(dst, src, pitch)

        EventManager.emit('fb/dirty', (x,y,width,height))

        return NL_OK

