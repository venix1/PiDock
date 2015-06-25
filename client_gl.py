#!/usr/bin/env python3.4

import asyncio
import ctypes
import msgpack
import os
import sys
import sdl2

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

        self.get_client(8, 3, 4)
        self.set_listenPort(5400)

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
        width = self.width
        height = self.height
        #depth = self.format.bitsPerPixel
        depth = 32

        self.window = sdl2.SDL_CreateWindow(b"Hello World",
                              sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
                              width, height, sdl2.SDL_WINDOW_SHOWN)

        self.surface = sdl2.SDL_GetWindowSurface(self.window)
        # No good way to do this sanely!!!
        # So we just send the pointer address and hope it casts
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

    def got_framebuffer_update(self, x, y, w, h):
        sdl2.SDL_UpdateWindowSurface(self.window)
        #sdl2.SDL_UpdateWindowSurfaceRects(self.window)



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

asyncio.get_event_loop().run_until_complete(run(instance.main_loop))
#asyncio.get_event_loop().run_forever()

sys.exit(0)
