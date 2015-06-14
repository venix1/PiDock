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

import rpigl.gles2 as gl

from event import EventManager

event_table = {}

def run(fn, *args):
    while fn(*args):
        yield from asyncio.sleep(0)

# A GLSL (GL Shading Language)  program consists of at least two shaders:
# a vertex shader and a fragment shader.
# Here is the vertex shader.
vertex_glsl = """
attribute vec4 vertex; // an attribute is a vertex-specific input to the vertex shader
attribute vec2 uvIn; // an attribute is a vertex-specific input to the vertex shader
varying vec2 uvOut;  // a varying is output to the vertex shader and input to the fragment shader
void main(void) {
  uvOut.x = (vertex.x + 1.0) * 0.5;
  uvOut.y = (-vertex.y + 1.0) * 0.5;

  // uvOut = uvIn; // WTF?? This changes gl_Position 

  gl_Position = vertex;
}
"""

# Here is the fragment shader
fragment_glsl = """
uniform sampler2D texture; // access the texture
varying vec2 uvOut;  // a varying is output to the vertex shader and input to the fragment shader
void main(void) {
  gl_FragColor = texture2D(texture, uvOut);
}
"""



class SDLRFBClient(rfb.rfbClient):
    def __init__(self):
        rfb.rfbClient.__init__(self)
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.get_client(5, 3, 2)
        self.set_listenPort(5400)

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
        width = self.width
        height = self.height
        #depth = self.format.bitsPerPixel
        depth = 32

        self.window = sdl2.SDL_CreateWindow(b"Hello World",
                              sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
                              width, height, sdl2.SDL_WINDOW_OPENGL)
        assert self.window, "Window failed"

        self.glcontext = sdl2.SDL_GL_CreateContext(self.window)

        # mode = sdl2.SDL_DisplayMode()
        # sdl2.SDL_GetWindowDisplayMode(self.window, mode)
        # mode.format = sdl2.SDL_PIXELFORMAT_BGR888
        # sdl2.SDL_SetWindowDisplayMode(self.window, mode)
    
        #self.surface = sdl2.SDL_GetWindowSurface(self.window)
        #self.surface = sdl2.SDL_CreateRGBSurface(0, 1920, 1080, 32, 0xff, 0xff00, 0xff0000, 0xff000000)
        #self.surface = sdl2.SDL_CreateRGBSurface(0, 1920, 1080, 16, 0x1F, 0x3e0, 0x7C00, 0)
        self.surface = sdl2.SDL_CreateRGBSurface(0, 1920, 1080, 16, 0, 0, 0, 0)

        # TODO: Replace with memoryview support
        # So we just send the pointer address and hope it casts

        self.set_framebuffer_from_ptr(self.surface.contents.pixels)

        self.texture = ctypes.c_uint(0)
        gl.glGenTextures(1, ctypes.byref(self.texture))

        self.program = gl.glCreateProgram()

        shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(shader, 1, ctypes.c_char_p(vertex_glsl.encode('utf-8')), None)
        gl.glCompileShader(shader)
        status = ctypes.c_int()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(value))
            log = ctypes.create_string_buffer(value.value)
            length = ctypes.c_size_t(value.value)
            print(log, ctypes.byref(log), ctypes.c_char_p(ctypes.addressof(log)))
            gl.glGetProgramInfoLog(self.program, length, ctypes.byref(length), ctypes.c_char_p(ctypes.addressof(log)))
            print(log.raw)
            raise Exception('Program linking failed')
        gl.glAttachShader(self.program, shader)

        shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(shader, 1, ctypes.c_char_p(fragment_glsl.encode('utf-8')), None)
        gl.glCompileShader(shader)
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(value))
            log = ctypes.create_string_buffer(value.value)
            length = ctypes.c_size_t(value.value)
            print(log, ctypes.byref(log), ctypes.c_char_p(ctypes.addressof(log)))
            gl.glGetProgramInfoLog(self.program, length, ctypes.byref(length), ctypes.c_char_p(ctypes.addressof(log)))
            print(log.raw)
            raise Exception('Program linking failed')
        gl.glAttachShader(self.program, shader)

        gl.glLinkProgram(self.program)
        gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS, ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetProgramiv(self.program, gl.GL_INFO_LOG_LENGTH, ctypes.byref(value))
            log = ctypes.create_string_buffer(value.value)
            length = ctypes.c_size_t(value.value)
            print(log, ctypes.byref(log), ctypes.c_char_p(ctypes.addressof(log)))
            gl.glGetProgramInfoLog(self.program, length, ctypes.byref(length), ctypes.c_char_p(ctypes.addressof(log)))
            print(log.raw)
            raise Exception('Program linking failed')

       
        self.vbo = ctypes.c_uint()
        self.ibo = ctypes.c_uint()
        gl.glGenBuffers(1, ctypes.byref(self.vbo))
        gl.glGenBuffers(1, ctypes.byref(self.ibo))

        vertices = [
            -1, -1, 0, 0, 0, 
            -1,  1, 0, 0, 1,
             1,  1, 0, 1, 1,
             1, -1, 0, 1, 0,
        ]
        array = (ctypes.c_float * len(vertices))(*vertices)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo);
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices)*4, array, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        indices = [ 0, 1, 2, 0, 2, 3]
        array = (ctypes.c_ubyte * len(indices))(*indices)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo);
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(indices), array, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        # Setup texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR); 
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE);
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE);

        # fp = open('/dev/fb0', 'r+b')
        # self.fb = mmap.mmap(fp.fileno(), 1920*1080*2)
        # fb_ptr = memoryview(self.fb)
        # self.set_framebuffer_from_ptr(fb_ptr)


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

        # gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, x, y, width, height, gl.GL_RGBA,
        #     gl.GL_UNSIGNED_BYTE, self.surface.contents.pixels)
        # gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def finished_framebuffer_update(self):
        clock = time.time()
        # gl.glClearColor(1,1,1,1)
        # gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0, gl.GL_RGBA,
        #     gl.GL_UNSIGNED_BYTE, self.surface.contents.pixels)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0, gl.GL_RGBA,
            gl.GL_UNSIGNED_SHORT_5_5_5_1, self.surface.contents.pixels)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        gl.glValidateProgram(self.program)
        gl.glUseProgram(self.program);

        tex = gl.glGetUniformLocation(self.program, "texture".encode('utf-8'));
        gl.glActiveTexture(gl.GL_TEXTURE0);
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture);
        gl.glUniform1i(tex, 0);

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo);
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 20, 0)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 20, 12)
        gl.glEnableVertexAttribArray(0)
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_BYTE, 0);

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0);
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glUseProgram(0); 

        sdl2.SDL_GL_SwapWindow(self.window)
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
