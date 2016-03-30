#!/usr/bin/env python3.4
"""Display exported framebuffer using SDL."""

import asyncio
import ctypes
import msgpack
import signal
import sdl2
import time

import pyzre
import rfb

from base64 import b64encode
from pidock.edid import EDID, MonitorRangeDescriptor, MonitorNameDescriptor
from pidock.edid import MonitorSerialDescriptor
from math import ceil

MODELINE_1080P = \
    '"1920x1080" 148.500 1920 2008 2052 2200 1080 1084 1089 1125 +hsync +vsync'

# Information required to convert SDL2 format to VNC settings.
SDL_PIXELFORMATS = {
    # 16 bit formats

    # 24/32 bit formats
    sdl2.SDL_PIXELFORMAT_RGB888:   {
        'name': 'SDL_PIXELFORMAT_RGB888',
        'bitsPerSample': 8,
        'samplesPerPixel': 3,
        'bytesPerPixel':  4,
        'redShift': 0,
        'greenShift': 8,
        'blueShift': 16
    },
    sdl2.SDL_PIXELFORMAT_RGBX8888: 'SDL_PIXELFORMAT_RGBX8888',
    sdl2.SDL_PIXELFORMAT_BGR888:   'SDL_PIXELFORMAT_BGR888',
    sdl2.SDL_PIXELFORMAT_BGRX8888: 'SDL_PIXELFORMAT_BGRX8888',
    sdl2.SDL_PIXELFORMAT_ARGB8888: 'SDL_PIXELFORMAT_ARGB8888',
    sdl2.SDL_PIXELFORMAT_RGBA8888: 'SDL_PIXELFORMAT_RGBA8888',
    sdl2.SDL_PIXELFORMAT_ABGR8888: 'SDL_PIXELFORMAT_ABGR8888',
    sdl2.SDL_PIXELFORMAT_BGRA8888: 'SDL_PIXELFORMAT_BGRA8888',
}


class SDLRFBClient(rfb.rfbClient):
    """pyVNC client for SDL rendering."""

    def __init__(self, display):
        """constructor.  Requres SDL display."""
        rfb.rfbClient.__init__(self)

        self.modes = []
        mode = sdl2.SDL_DisplayMode()

        # How to get DPI? Native call for screen dimensions?
        for i in range(sdl2.SDL_GetNumDisplayModes(display)):
            sdl2.SDL_GetDisplayMode(display, i, ctypes.byref(mode))
            if mode.format in SDL_PIXELFORMATS:
                self.modes.append((mode.w, mode.h,
                                   SDL_PIXELFORMATS[mode.format]))

        sdl2.SDL_GetCurrentDisplayMode(display, mode)
        assert mode.format in SDL_PIXELFORMATS, 'Unsupported mode'
        assert isinstance(SDL_PIXELFORMATS[mode.format], dict), \
            'Format not implemented'
        self.mode = (mode.w, mode.h, SDL_PIXELFORMATS[mode.format])

        # Attempt to pull edid
        # else generate based on modes.
        self.edid = EDID()
        self.edid.add_modeline(MODELINE_1080P)
        self.edid.add_descriptor(MonitorRangeDescriptor(
            (50, 122), (24, 140), 290))
        self.edid.add_descriptor(MonitorNameDescriptor('PiDockVirtual'))
        self.edid.add_descriptor(MonitorSerialDescriptor('PiDockV000000'))

        self.edid.red = (0.642, 0.345)
        self.edid.green = (0.292, 0.596)
        self.edid.blue = (0.144, 0.125)
        self.edid.white = (0.312, 0.328)

        # with open('edid.bin', 'wb') as fp:
        #     fp.write(self.edid.asBytes())

        # self.edid.add_modeline('"{}x{}" {} {}
        # self.edid.add_mode(self.mode[0], self.mode[1], 60)
        # for mode in self.modes:
        #     # Force 60hz for now.  Unlikely to ever support more
        #     self.edid.add_mode(mode[0], mode[1], 60)

        self.get_client(8, 3, 4)
        self.set_listenPort(5400)

        print('JPEG: ', self.enableJPEG)
        # self.enableJPEG = False
        print('JPEG: ', self.enableJPEG)
        # self.redShift = 11
        # self.greenShift = 6
        # self.blueShift = 1

        self.clock = time.time()

    def update(self):
        """Poll and process RFB and SDL events."""
        if self.isActive() and self.WaitForMessage():
            if not self.HandleRFBServerMessage():
                return False

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                return False

        return True

    def malloc_framebuffer(self):
        """pyVNC framebuffer creation."""
        print("Creating framebuffer")
        print(self.width, self.height)
        width = self.width
        height = self.height
        # depth = self.format.bitsPerPixel
        depth = 32
        self.pitch = width * ceil(depth/8)
        assert depth == 32, 'Only 32bpp supported'

        self.window = sdl2.SDL_CreateWindow(
            b"PiDock", sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width, height, 0)
        assert self.window, "Window failed: " + str(sdl2.SDL_GetError())

        self.surface = sdl2.SDL_GetWindowSurface(self.window)
        # TODO: Replace with memoryview support
        # Needs convert pixels to memoryview
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

        self.clock = time.time()

        return True

    def got_framebuffer_update(self, x, y, width, height):
        """pyVNC event handler."""
        # print('got_framebuffer_update: %d %d %d %d' % (x,y,width,height))

        # rect = sdl2.SDL_Rect(x, y, width, height)
        # sdl2.SDL_UpdateWindowSurfaceRects(self.window, rect, 1)
        pass

    def finished_framebuffer_update(self):
        """pyVNC event handler."""
        clock = time.time()

        sdl2.SDL_UpdateWindowSurface(self.window)

        from math import ceil
        diff = time.time() - clock
        print('Frame: {:.0f}ms'.format(ceil(diff*1000)))
        print('Overhead: {:.0f}ms'.format(
            ceil((time.time() - self.clock - diff)*1000))
        )
        print('FPS: {:.0f}'.format(1/(time.time() - self.clock)))
        self.clock = time.time()


class SDLSink(pyzre.ZRE):
    """Framebuffer sink using SDL."""

    def __init__(self, loop):
        """constructor.  Require asyncio loop."""
        # Initialize SDL displays

        self.outputs = []

        display_count = sdl2.SDL_GetNumVideoDisplays()
        print('SDL_GetNumVideoDisplays():', display_count)

        for display in range(sdl2.SDL_GetNumVideoDisplays()):
            self.outputs.append(SDLRFBClient(display))

        pyzre.ZRE.__init__(self, loop=loop)
        self.broadcast()

    def main_loop(self):
        """update all output."""
        for screen in self.outputs:
            screen.update()
        return True

    def on_hello(self, peer, msg):
        """ZRE hello event handler."""
        print('on_hello:', peer, msg)

        # Send current display mode
        # TODO: Handle multiple outputs
        msg = {
            'op': 'display',
            'mode': self.outputs[0].mode,
            'modes': self.outputs[0].modes,
            'edid': b64encode(self.outputs[0].edid.asBytes())
        }
        self.whisper(peer, msgpack.packb(msg))

    # ZRE event handlers
    def on_whisper(self, peer, msg):
        """ZRE whisper event handler."""
        content = msgpack.unpackb(msg.content, encoding='utf-8')

        if content.get('op', None) == 'connect':
            # size = (content['width'], content['height'])
            # bpp = content['bpp']

            # Configure output to match mode

            msg = {
                'op': 'ready',
                'ip': self.ip,
                'port': self.outputs[0].listenPort
            }

            self.whisper(peer, msgpack.packb(msg))
            self.outputs[0].listen(-1)
        else:
            raise Exception('Unhandled msg:' + str(msg))


def run(fn, *args):
    """execute and yield function while True is returned."""
    while fn(*args):
        yield from asyncio.sleep(0)


def main(args):
    """module entrypoint."""
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

    # TODO. Check SDL_GetNumVideoDisplays and create an instance for each
    # outputs = sdl2.SDL_GetNumVideoDisplays()
    instance = SDLSink(asyncio.get_event_loop())

    def signal_handler(signal, frame):
        asyncio.get_event_loop().stop()
        return 0

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.get_event_loop().run_until_complete(run(instance.main_loop))

    return 0
