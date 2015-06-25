#!/usr/bin/env python3.4

import asyncio
import ctypes
import msgpack
import os
import signal
import sys
import time

import pyzre
import rfb
import videocore as vc


from event import EventManager

event_table = {}

def run(fn, *args):
    while fn(*args):
        yield from asyncio.sleep(0)

class RFBClient(rfb.rfbClient):
    def __init__(self):
        rfb.rfbClient.__init__(self)

        self.get_client(8, 3, 4)
        self.set_listenPort(5400)

        self.clock = time.time()

    def update(self):
        if self.isActive() and self.WaitForMessage():
            if not self.HandleRFBServerMessage():
                return False

        return True

    def malloc_framebuffer(self):
        print("Creating framebuffer")
        width = self.width
        height = self.height
        #depth = self.format.bitsPerPixel
        depth = 32
        pitch = self.width * int(depth/8)

        vc.bcm_host_init()

        self.display = vc.Display(0)
        assert self.display, 'Display init failed'

        self.img = vc.Resource(vc.VC_IMAGE_BGRX8888, pitch, height)

        self.img_data = bytearray(pitch*height)
        # for y in range(height):
        #     for x in range(pitch):
        #         self.img_data[pitch*y+x+0] = (y % 2) * 255
        self.framebuffer = self.img_data
        # import ctypes
        # self.set_framebuffer_from_ptr(ctypes.addressof(ctypes.c_void_p.from_buffer(self.img_data)))
        
        # self.old_img_data = self.img_data


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
        print('got_framebuffer_update: (%d, %d) - (%d, %d)' %(x,y,width,height))
        if not self.clock:
            self.clock = time.time()
        depth = 32
        # width = self.width
        # height = self.height
        pitch = width * int(depth/8)

        # for y in range(int(height/2)):
        #     for x in range(width):
        #         self.img_data[pitch*y+x+0] = 255
        #         self.img_data[pitch*y+x+1] = 255
        #         self.img_data[pitch*y+x+2] = 255
        #         self.img_data[pitch*y+x+3] = 255
        #print('BEGIN write_data')
        # self.clock = time.time()
        # TODO replace with change
        self.img.write_data(vc.VC_IMAGE_BGRX8888, pitch, self.img_data, vc.Rect(x,y,width,height))
        # print('END write_data - time: ' + str(time.time() - self.clock))
        # with open('img.data', 'wb') as fp:
        #     fp.write(self.img_data)

    def finished_framebuffer_update(self):
        x = 0
        y = 0
        width = self.width
        height = self.height
        with vc.Update(0) as update:
            # self.element = self._update.add_element(self.display, 
            #     vc.Rect(0,0, 1920, 1080), self.img, vc.Rect(x,y,1920,180), 
            #     vc.DISPMANX_PROTECTION_NONE, None, None, vc.DISPMANX_NO_ROTATE)
            
            if hasattr(self, 'element') and self.element:
                self.element.modified(update, vc.Rect(x,y,width,height))
            else:
                self.element = update.add_element(self.display, 1000,
                    vc.Rect(0,0, self.width, self.height), self.img, vc.Rect(0,0,self.width, self.height), 
                    vc.DISPMANX_PROTECTION_NONE, vc.DISPMANX_NO_ROTATE)
        print('Frame: ' + str(time.time() - self.clock))
        # self.clock = time.time()
        self.clock = None

class Sink(pyzre.ZRE):
    def __init__(self, loop):
        pyzre.ZRE.__init__(self, loop=loop)

        self.screen = RFBClient()

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
