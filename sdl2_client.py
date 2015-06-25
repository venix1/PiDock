#!/usr/bin/env python3.4

import asyncio
import ctypes
import mmap
import msgpack
import os
import signal
import sys
import sdl2
import time

import pyzre
import rfb

from event import EventManager

event_table = {}

def run(fn, *args):
    while fn(*args):
        yield from asyncio.sleep(0)

class SDLRFBClient(rfb.rfbClient):
    def __init__(self):
        rfb.rfbClient.__init__(self)
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.get_client(5, 3, 2)
        self.set_listenPort(5400)
        self.enableJPEG = False

        self.clock = time.time()

    def update(self):
        if self.isActive() and self.WaitForMessage():
            if not self.HandleRFBServerMessage():
                return False

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                running = False
                return False

        return True

    def malloc_framebuffer(self):
        print("Creating framebuffer")
        print(self.width, self.height)
        # width = self.width
        # height = self.height
        width = 1920
        height = 1080
        #depth = self.format.bitsPerPixel
        depth = 16

        self.window = sdl2.SDL_CreateWindow(b"Hello World",
                              sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
                              width, height, sdl2.SDL_WINDOW_OPENGL)
        assert self.window, "Window failed: " + str(sdl2.SDL_GetError())

        # mode = sdl2.SDL_DisplayMode()
        # sdl2.SDL_GetWindowDisplayMode(self.window, mode)
        # mode.format = sdl2.SDL_PIXELFORMAT_ABGR1555
        # sdl2.SDL_SetWindowDisplayMode(self.window, mode)
    
        self.surface = sdl2.SDL_GetWindowSurface(self.window)

        self.set_framebuffer_from_ptr(self.surface.contents.pixels)

        # Make sure VNC and SDL match formatting
        # client->format.bitsPerPixel=depth;
        # client->format.redShift=sdl->format->Rshift;
        # client->format.greenShift=sdl->format->Gshift;
        # client->format.blueShift=sdl->format->Bshift;
        # client->format.redMax=sdl->format->Rmask>>client->format.redShift;
        # client->format.greenMax=sdl->format->Gmask>>client->format.greenShift;
        # client->format.blueMax=sdl->format->Bmask>>client->format.blueShift;
        # self.SetFormatAndEncodings(client);

        return True

    def got_framebuffer_update(self, x, y, width, height):
        # print('got_framebuffer_update: %d %d %d %d' % (x,y,width,height))
        if not self.clock:
            self.clock = time.time()

    def finished_framebuffer_update(self):
        clock = time.time()

        # pixels = ctypes.cast(self.surface.contents.pixels, ctypes.POINTER(ctypes.c_short))
        # print('{:016b}'.format(1)) 
        # for i in range(16):
        #     print('{0}: {1:016b}'.format(i, pixels[i])) 

        sdl2.SDL_UpdateWindowSurface(self.window)

        print('Frame: ' + str(time.time() - clock))
        print('Overhead: ' + str(time.time() - self.clock))
        self.clock = None

class Sink(pyzre.ZRE):
    def __init__(self, loop):
        pyzre.ZRE.__init__(self, loop=loop)

        self.screen = SDLRFBClient()

        self.broadcast()

    
    def main_loop(self):
        return self.screen.update()

    def on_hello(self, peer, msg):
        pass

    # ZRE event handlers
    def on_whisper(self, peer, msg):
        print(type(msg), msg)
        content = msgpack.unpackb(msg.content, encoding='utf-8')
        print(content)

        if content.get('op', None) == 'connect':
            size = (content['width'], content['height'])

            
            msg = {
                'op': 'ready',
                'ip': self.ip,
                'port': self.screen.listenPort
            }

            self.whisper(peer, msgpack.packb(msg))
            self.screen.listen(-1)
        else:        
            raise Exception('Unhandled msg:' + str(msg))

instance = Sink(asyncio.get_event_loop())

# def event_loop():
#     while True:
#         EventManager.update()
#         yield from asyncio.sleep(0)

def signal_handler(signal, frame):
    asyncio.get_event_loop().stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

asyncio.get_event_loop().run_until_complete(run(instance.main_loop))
#asyncio.get_event_loop().run_forever()

sys.exit(0)
