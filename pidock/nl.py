"""Netlink interface to PiDock kernel module."""

import ctypes
import socket
import struct

# import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from libnl.attr import nla_len
from libnl.errno_ import NLE_AGAIN
from libnl.handlers import NL_CB_CUSTOM, NL_CB_SEQ_CHECK, NL_CB_VALID, NL_OK
from libnl.msg import nlmsg_hdr
from libnl.nl import nl_recvmsgs_default
from libnl.socket_ import nl_socket_add_memberships, nl_socket_alloc
from libnl.socket_ import nl_socket_modify_cb
from libnl.genl.ctrl import genl_ctrl_resolve, genl_ctrl_resolve_grp
from libnl.genl.genl import genl_connect, genlmsg_parse

from event import EventManager


def noop_seq_check(msg, _):
    """Discard netlink sequence verification."""
    return NL_OK


class Connector(object):
    """Proxy to kernel pidock_connector structure."""

    def __init__(self):
        """constructor."""
        pass


class PiDockConnection(object):
    """Proxy to kernel pidock_connection structure."""

    def __init__(self, framebuffer):
        """Initialize with framebuffer."""
        self.framebuffer = framebuffer
        self.sk = nl_socket_alloc()
        sk = self.sk

        # configure callbacks, disable sequence checking
        nl_socket_modify_cb(sk, NL_CB_SEQ_CHECK, NL_CB_CUSTOM, noop_seq_check,
                            None)
        ptr = ctypes.addressof(ctypes.c_void_p.from_buffer(framebuffer))
        nl_socket_modify_cb(sk, NL_CB_VALID, NL_CB_CUSTOM, self.recvmsg, ptr)

        rc = genl_connect(sk)
        assert rc == 0, 'Failed to connect socket'

        family = genl_ctrl_resolve(sk, b'pidock')
        group = genl_ctrl_resolve_grp(sk, b'pidock', b'pidock_mc_group')
        print('family: %d\tgroup: %d' % (family, group))

        # Set buffers to handle large payloads
        sk.socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                      33554432)
        sk.s_bufsize = 32*4096

        # nl_socket_set_nonblocking(sk)
        sk.socket_instance.setblocking(0)
        nl_socket_add_memberships(sk, group, 0)

    def run_once(self):
        """Poll netlink queue for new messages."""
        rc = nl_recvmsgs_default(self.sk)
        if rc < 0 and rc != -NLE_AGAIN:
            print('Error: ' + str(rc))

    def load_edid(self, edid):
        """Send netlink message to load EDID."""
        pass
        # skb = genlmsg_new(len + 32, GFP_KERNEL)
        # msg_head = genlmsg_put(skb, 0, 0, &pidock_gnl_family 0, PIDOCK_EDID)
        # nla_put(sizeof edid)

    def add_connector(self, connector):
        """Send netlink message to add connector."""
        pass

    def remove_connector(self, connector):
        """Send netlink message to remove connector."""
        pass

    @staticmethod
    def recvmsg(msg, fb):
        """Receive and parse netlink message."""
        # print('Got Message')
        nlh = nlmsg_hdr(msg)
        tb = [None] * 10

        # TODO: Expect multiple messages from libnl

        rc = genlmsg_parse(nlh, 0, tb, 5, None)
        assert rc == 0, 'genlmsg_parse failed: ' + str(rc)

        x, y, width, height, pitch = \
            struct.unpack('IIIII', tb[2].payload[:nla_len(tb[2])])
        # print('Dirty: (%d, %d)  (%d, %d) %d' % (x,y,width,height, pitch))

        data = tb[3].payload[:nla_len(tb[3])]
        scanline = 1680*4
        offset = scanline * y + x

        assert len(data) >= pitch, \
            '%d %d %d %d %d' % (x, y, width, height, pitch)

        for h in range(height):
            line = pitch*h
            # Using c_void_p type causes segfault!!
            # dst = ctypes.c_void_p.from_address(fb + offset + line)
            # src = ctypes.c_void_p.from_buffer(data[line:])
            dst = fb + offset + scanline * h
            src = ctypes.addressof(ctypes.c_void_p.from_buffer(data[line:]))
            ctypes.memmove(dst, src, pitch)

        EventManager.emit('fb/dirty', (x, y, width, height))

        return NL_OK
