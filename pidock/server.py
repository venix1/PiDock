#!/usr/bin/env python
"""Export framebuffer object over VNC."""

# flake8: noqa: ignore=E702

import asyncio
import libdrm
import msgpack
import pidock.nl
import sys
import time

from pidock.event import EventManager
from pyzre.zre import ZRE

from base64 import b64decode

import pyximport; pyximport.install()
import pidock.crc32
from pidock.jpeg_encoder import JPEGEncoder

event_table = {}

def run(fn, *args):
    """Run a function indefinately as long as it returns True."""
    while fn(*args):
        yield from asyncio.sleep(0)


class Source(ZRE):
    """Class representing framebuffer output."""

    def __init__(self, loop):
        """constructor.  requires asyncio loop object."""
        ZRE.__init__(self, loop)

        self.drm = libdrm.DRMCard('/dev/dri/card1')
        self.drm.refresh()
        # if self.drm.count_fbs < 1:
        #     sys.exit(1)
        r = self.drm.get_fb(27)
        print(r)
        size = r['height'] * r['pitch']

        r = self.drm.map_dumb(1)
        print(r)

        self.fb = self.drm.mmap64(size, r['offset'])
        print(self.fb)

        # TODO: Get resolution from DRM
        # For now deafult to 1920x1080 and resize later

        self.width = 1920
        self.height = 1080

        # self.fb = bytearray(self.width*self.height*4)
        self.server = JPEGEncoder([], self.width, self.height, 8, 3, 4,
                                    self.fb)

        # Framebuffer BGRA
        # self.server.redShift = 16
        # self.server.greenShift = 8
        # self.server.blueShift = 0

        self.pidock = pidock.nl.PiDockSocket(self.fb)

        self.clock = time.time()

        EventManager.register('fb/damage', self.on_damage)

    def on_damage(self, args):
        """EventManager callback for 'fb/damage' event."""
        print(args)
        x, y, w, h = args
        x2 = x + w
        y2 = y + h
        # Not receiving full update.
        # for testing we override.
        # self.server.mark_rect_as_modified(x, y, x2, y2)
        self.server.mark_rect_as_modified(0, 0, self.width, self.height) 

    def main_loop(self):
        """main processing function."""
        if self.server.is_active:
            self.pidock.run_once()

            EventManager.update()

            # Fix to 60 FPS
            if time.time() - self.clock < .015:
                return True
            # 1 FPS
            if time.time() - self.clock < 1:
                return True

            # self.server.fillRect((0,0), (200,200), 0xFFFFFFFF)
            # self.server.markRectAsModified((0, 0), (self.width, self.height))
            self.server.process_events(0)
            # time.sleep(1)

        return True

    def on_hello(self, peer, msg):
        """handler for ZRE hello message."""
        self.hello(peer)
        msg = {
            'op': 'connect',
            'width': 1680,
            'height': 1050
        }
        self.whisper(peer, msgpack.packb(msg))

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
