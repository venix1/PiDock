"""Netlink interface to PiDock kernel module."""

import ctypes
import socket
import struct

# import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from libnl.attr import nla_len, nla_put_u32, nla_get_u32
from libnl.errno_ import NLE_AGAIN
from libnl.handlers import NL_CB_CUSTOM, NL_CB_SEQ_CHECK, NL_CB_VALID, NL_OK
from libnl.msg import nlmsg_hdr, nlmsg_alloc
from libnl.nl import nl_recvmsgs_default, nl_send_auto, NL_AUTO_PORT
from libnl.nl import NL_AUTO_SEQ
from libnl.socket_ import nl_socket_add_memberships, nl_socket_alloc
from libnl.socket_ import nl_socket_modify_cb
from libnl.genl.ctrl import genl_ctrl_resolve, genl_ctrl_resolve_grp
from libnl.genl.genl import genl_connect, genlmsg_parse, genlmsg_put
from libnl.genl.genl import genlmsg_hdr

from .event import EventManager

PIDOCK_A_UNSPEC = 0
PIDOCK_A_TILE_RECT = 1
PIDOCK_A_TILE_DATA = 2
PIDOCK_A_OUTPUT_ID = 3
PIDOCK_A_FB_ID = 4

PIDOCK_A_MAX = 4

PIDOCK_C_FB_DIRTY = 0
PIDOCK_C_FB_REFRESH = 1
PIDOCK_C_CONNECTOR_ADD = 2
PIDOCK_C_CONNECTOR_REMOVE = 3
PIDOCK_C_GETFB = 4


def noop_seq_check(msg, _):
    """Discard netlink sequence verification."""
    return NL_OK


class PiDockConnector(object):
    """Proxy to kernel pidock_connector structure."""

    def __init__(self):
        """constructor."""
        pass


class PiDockSocket(object):
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

        self.family = genl_ctrl_resolve(sk, b'pidock')
        self.group = genl_ctrl_resolve_grp(sk, b'pidock', b'pidock_mc_group')
        print('family: %d\tgroup: %d' % (self.family, self.group))

        # Set buffers to handle large payloads
        sk.socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                      33554432)
        sk.s_bufsize = 32*4096

        # nl_socket_set_nonblocking(sk)
        sk.socket_instance.setblocking(0)
        nl_socket_add_memberships(sk, self.group, 0)

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
        msg = nlmsg_alloc()
        genlmsg_put(msg, NL_AUTO_PORT, NL_AUTO_SEQ, self.family,
                    0, 0, PIDOCK_C_CONNECTOR_ADD, 0)

        nla_put_u32(msg, PIDOCK_A_OUTPUT_ID, 1337)

        rc = nl_send_auto(self.sk, msg)
        if rc:
            assert False, rc

    def getfb(self, output):
        """Get associated framebuffer id for output."""
        msg = nlmsg_alloc()
        genlmsg_put(msg, NL_AUTO_PORT, NL_AUTO_SEQ, self.family,
                    0, 0, PIDOCK_C_GETFB, 0)

        nla_put_u32(msg, PIDOCK_A_OUTPUT_ID, 0)
        rc = nl_send_auto(self.sk, msg)

        if rc < 0:
            raise Exception('failed')

        # asyncio.Future

    def remove_connector(self, connector):
        """Send netlink message to remove connector."""
        pass

    @staticmethod
    def recvmsg(msg, fb):
        """Receive and parse netlink message."""
        # print('Got Message')
        nlh = nlmsg_hdr(msg)
        info = genlmsg_hdr(nlh)
        cmd = info[0]

        # print(cmd)
        tb = [None] * (PIDOCK_A_MAX+1)

        # TODO: Expect multiple messages from libnl

        rc = genlmsg_parse(nlh, 0, tb, PIDOCK_A_MAX, None)
        assert rc == 0, 'genlmsg_parse failed: ' + str(rc)

        if cmd == PIDOCK_C_FB_DIRTY:
            r_msg = tb[PIDOCK_A_TILE_RECT]
            x, y, width, height, pitch = \
                struct.unpack('IIIII', r_msg.payload[:nla_len(r_msg)])
            fb_id = nla_get_u32(tb[PIDOCK_A_FB_ID])

            EventManager.emit('fb/damage', (x, y, width, height))
        elif cmd == PIDOCK_C_GETFB:
            fb_id = nla_get_u32(tb[PIDOCK_A_FB_ID])

            EventManager.emit('output/fb', fb_id)
        else:
            print('Cmd:', cmd)

        return NL_OK
