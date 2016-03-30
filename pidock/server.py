#!/usr/bin/env python
"""Export framebuffer object over VNC."""

import asyncio
import msgpack
import sys
import time

import pyzre
import rfb
import pidock_nl

from base64 import b64decode

event_table = {}


def run(fn, *args):
    """Run a function indefinately as long as it returns True."""
    while fn(*args):
        yield from asyncio.sleep(0)


class Source(pyzre.ZRE):
    """Class representing framebuffer output."""

    def __init__(self, loop):
        """constructor.  requires asyncio loop object."""
        pyzre.ZRE.__init__(self, loop)

        # fp = open('/dev/fb1', 'r+b')
        # print(fp.fileno())
        # self.fb = mmap.mmap(fp.fileno(), 1680*1050*4)
        # fb_ptr = memoryview(self.fb)

        # TODO: Get resolution from DRM
        # For now deafult to 1920x1080 and resize later

        self.width = 1920
        self.height = 1080

        self.fb = bytearray(self.width*self.height*4)
        self.server = rfb.rfbServer([], self.width, self.height, 8, 3, 4,
                                    self.fb)

        # Framebuffer BGRA
        # self.server.redShift = 16
        # self.server.greenShift = 8
        # self.server.blueShift = 0

        self.pidock = pidock_nl.PiDockConnection(self.fb)

        self.clock = time.time()

    def main_loop(self):
        """main processing function."""
        if self.server.isActive():
            self.pidock.run_once()

            # Fix to 60 FPS
            if time.time() - self.clock < .015:
                return True

            # self.server.fillRect((0,0), (200,200), 0xFFFFFFFF)
            self.server.markRectAsModified((0, 0), (self.width, self.height))
            self.server.processEvents(0)
            # time.sleep(1)

        return True

    def on_hello(self, peer, msg):
        """handler for ZRE hello message."""
        self.hello(peer)

    def on_whisper(self, peer, msg):
        """handler for ZRE whisper message."""
        print(type(msg), msg)
        content = msgpack.unpackb(msg.content, encoding='utf-8')
        print(content)

        op = content.get('op', None)
        if op == 'ready':
            time.sleep(1)
            # TODO: Solve race issue if client is slow setting up port.
            # Really client should set this up before sending packet
            self.server.reverseConnection(content['ip'], content['port'])
        elif op == 'display':
            edid = b64decode(content['edid'])
            self.pidock.load_edid(edid)

            msg = {
                'op': 'connect',
            }
            self.whisper(peer, msgpack.packb(msg))
        else:
            raise Exception('Unkown op:' + str(op))

instance = Source(asyncio.get_event_loop())

# def event_loop():
#     while True:
#         EventManager.update()
#         yield from asyncio.sleep(0)

asyncio.get_event_loop().run_until_complete(run(instance.main_loop))
# asyncio.get_event_loop().run_forever()

sys.exit(0)
