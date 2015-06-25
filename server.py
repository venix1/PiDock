#!/usr/bin/env python3.4

import asyncio
import ctypes
import msgpack
import os
import mmap
import sys
import time

import pyzre
import rfb
import pidock_nl

from event import EventManager

event_table = {}

def run(fn, *args):
    while fn(*args):
        yield from asyncio.sleep(0)

class Source(pyzre.ZRE):
    def __init__(self, loop):
        pyzre.ZRE.__init__(self, loop)

        # fp = open('/dev/fb1', 'r+b')
        # print(fp.fileno())
        # self.fb = mmap.mmap(fp.fileno(), 1680*1050*4)
        # fb_ptr = memoryview(self.fb)

        # TODO: Get resolution from DRM
        # For now deafult to 1920x1080 and resize later

        self.width = 1680
        self.height = 1050

        self.fb = bytearray(self.width*self.height*4)
        self.server = rfb.rfbServer([], self.width, self.height, 8, 3, 4, self.fb)

        # Framebuffer BGRA
        self.server.redShift = 16
        self.server.greenShift = 8
        self.server.blueShift = 0

        self.pidock = pidock_nl.PiDockConnection(self.fb)

        self.clock = time.time()

    def main_loop(self):
        if self.server.isActive():
            self.pidock.run_once()

            # Fix to 60 FPS
            if time.time() - self.clock < .015:
                return True

            #self.server.fillRect((0,0), (200,200), 0xFFFFFFFF)
            self.server.markRectAsModified((0,0), (self.width, self.height))
            self.server.processEvents(0)
            # time.sleep(1)

        return True

    def on_hello(self, peer, msg):
        self.hello(peer)

        msg = {
            'op': 'connect',
            'width': 640,
            'height': 480,
            'bpp': 4
        }


        self.whisper(peer, msgpack.packb(msg))

    def on_whisper(self, peer, msg):
        print(type(msg), msg)
        content = msgpack.unpackb(msg.content, encoding='utf-8')
        print(content)

        if content.get('op', None) == 'ready':
            time.sleep(1)
            # TODO: Solve race issue if client is slow setting up port. Really client should set this up before sending packet
            self.server.reverseConnection(content['ip'], content['port'])


instance = Source(asyncio.get_event_loop())

# def event_loop():
#     while True:
#         EventManager.update()
#         yield from asyncio.sleep(0)

asyncio.get_event_loop().run_until_complete(run(instance.main_loop))
#asyncio.get_event_loop().run_forever()

sys.exit(0)
