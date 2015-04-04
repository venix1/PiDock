#!/usr/bin/env python3.4

import asyncio
import os
import sys

import pyzre

zre = pyzre.ZRE()

#import rfb

#server = rfb.Server([], 400, 300, 8, 3, 4);
#server->frameBuffer=static_cast<char*>(malloc(400*300*4));
#server.runEventLoop()

asyncio.get_event_loop().run_forever()

sys.exit(0)
