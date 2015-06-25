#!/usr/bin/env python3.4

import os
import signal
import sys
import time

import videocore as vc

def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


clock = time.time()

print("Creating framebuffer")
width = 1920
height = 1080
#depth = format.bitsPerPixel
depth = 32
pitch = width * int(depth/8)

vc.bcm_host_init()

display = vc.Display(0)
assert display, 'Display init failed'


img_data = bytearray(pitch*height)
for y in range(height):
    for x in range(pitch):
        img_data[pitch*y+x+0] = (y % 2) * 255

# Example code. Does width | (pitch << 16).  No documentation why. Seems to make no difference
img = vc.Resource(vc.VC_IMAGE_RGBA32, pitch, height)

# What's with the artificial limit of 512x512?  Anything higher is blank.  Memory limits?
#   1920x48 = 92,160 is valid, but 640x480 = 307,200 is not.
print('Transfer Start')
clock = time.time()
img.write_data(vc.VC_IMAGE_RGBA32, pitch, img_data, vc.Rect(0,0,width,height))
print('Transfer Done: ' + str(time.time()-clock))

with vc.Update(0) as update:

    # Why does some example code do <<16 on dest width and height?
    # The use of << 16 is because VC wants this in highmem.  If it's not present, then size = 0(1)
    # with the scaling engine, this produces a single colored box.
    # Why does this still render a FULL WHITE BOX, when it should only be 64,16 at best
    # The first 4 colors are being applie to everything!?  The pointer in src_data is correct
    # but on passing, only the first color are acknowledged and applied. Tested by incrementing pointer
    # to second element which is red,. Then get a red bar.
    # WTF Is the point if it only copies the first value?
    # Scaling issue?  The reason why << 16 exists, because it expects the value in the high end?
    # Bingo!
    element = update.add_element(display, 1000,
        vc.Rect(0,0, width, height), img, vc.Rect(0,0,width,height), 
        vc.DISPMANX_PROTECTION_NONE, vc.DISPMANX_NO_ROTATE)

print('Transfer + Update: ' + str(time.time()-clock))

time.sleep(10)


sys.exit(0)
