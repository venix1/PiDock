#!/usr/bin/env python
"""Framebuffer sink using OpenGL."""

import asyncio
import ctypes
import msgpack
import signal
import sys
import sdl2
import time

import pyzre
import rfb

import rpigl.gles2 as gl

from math import ceil

event_table = {}

# A GLSL (GL Shading Language)  program consists of at least two shaders:
# a vertex shader and a fragment shader.
# Here is the vertex shader.
vertex_glsl = """
attribute vec4 vertex;
attribute vec2 uvIn;
varying vec2 uvOut;
void main(void) {
  uvOut.x = (vertex.x + 1.0) * 0.5;
  uvOut.y = (-vertex.y + 1.0) * 0.5;

  // uvOut = uvIn; // WTF?? This changes gl_Position

  gl_Position = vertex;
}
"""

# Here is the fragment shader
fragment_glsl = """
uniform sampler2D texture;
varying vec2 uvOut;
void main(void) {
  gl_FragColor = texture2D(texture, uvOut);
}
"""


class SDLRFBClient(rfb.rfbClient):
    """pyVNC SDL output client."""

    def __init__(self):
        """constructor."""
        rfb.rfbClient.__init__(self)
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        mode = sdl2.SDL_DisplayMode
        for i in range(sdl2.SDL_GetNumDisplayModes):
            sdl2.SDL_GetDisplayMode(0, i, ctypes.byref(mode))
            print(mode.w, mode.h)

        # SDL_GetNumDisplayModes
        # SDL_GetDisplayMode

        self.get_client(8, 3, 4)
        self.set_listenPort(5400)

        print('JPEG: ', self.enableJPEG)
        self.enableJPEG = False
        print('JPEG: ', self.enableJPEG)
        # self.redShift = 11
        # self.greenShift = 6
        # self.blueShift = 1

        self.clock = time.time()

    def update(self):
        """poll and process pyVNC and SDL2 events."""
        if self.isActive() and self.WaitForMessage():
            if not self.HandleRFBServerMessage():
                return False

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                return False

        return True

    def malloc_framebuffer(self):
        """pyVNC event handler."""
        print("Creating framebuffer")
        print(self.width, self.height)
        width = self.width
        height = self.height
        depth = self.format.bitsPerPixel
        self.pitch = width * ceil(depth/8)
        assert depth == 32, 'Only 32bpp supported'

        self.window = sdl2.SDL_CreateWindow(
            b"PiDock",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            width, height,
            sdl2.SDL_WINDOW_OPENGL)
        assert self.window, "Window failed: " + str(sdl2.SDL_GetError())

        self.glcontext = sdl2.SDL_GL_CreateContext(self.window)

        # mode = sdl2.SDL_DisplayMode()
        # sdl2.SDL_GetWindowDisplayMode(self.window, mode)
        # mode.format = sdl2.SDL_PIXELFORMAT_RGBA5551
        # sdl2.SDL_SetWindowDisplayMode(self.window, mode)

        self.surface = sdl2.SDL_CreateRGBSurface(0,
                                                 width, height, depth,
                                                 0, 0, 0, 0)

        # So we just send the pointer address and hope it casts
        # TODO: Replace with memoryview support
        self.set_framebuffer_from_ptr(self.surface.contents.pixels)

        self.texture = ctypes.c_uint(0)
        gl.glGenTextures(1, ctypes.byref(self.texture))

        self.program = gl.glCreateProgram()

        shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(shader, 1,
                          ctypes.c_char_p(vertex_glsl.encode('utf-8')),
                          None)
        gl.glCompileShader(shader)
        status = ctypes.c_int()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH,
                             ctypes.byref(value))

            log = ctypes.create_string_buffer(value.value)
            log_ptr = ctypes.c_char_p(ctypes.addressof(log))
            length = ctypes.c_size_t(value.value)
            length_ptr = ctypes.byref(length)

            gl.glGetShaderInfoLog(shader, length, length_ptr, log_ptr)
            print(log.raw)
            raise Exception('Shader(vertex) compilation failed')
        gl.glAttachShader(self.program, shader)

        shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(shader, 1,
                          ctypes.c_char_p(fragment_glsl.encode('utf-8')),
                          None)
        gl.glCompileShader(shader)
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH,
                             ctypes.byref(value))

            log = ctypes.create_string_buffer(value.value)
            log_ptr = ctypes.c_char_p(ctypes.addressof(log))
            length = ctypes.c_size_t(value.value)
            length_ptr = ctypes.byref(length)

            print(log, ctypes.byref(log),
                  ctypes.c_char_p(ctypes.addressof(log)))
            gl.glGetShaderInfoLog(shader, length, length_ptr, log_ptr)
            print(log.raw)
            raise Exception('Fragment shader compilation failed')
        gl.glAttachShader(self.program, shader)

        gl.glLinkProgram(self.program)
        gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS,
                          ctypes.byref(status))
        if not status:
            value = ctypes.c_int()
            gl.glGetProgramiv(self.program, gl.GL_INFO_LOG_LENGTH,
                              ctypes.byref(value))
            log = ctypes.create_string_buffer(value.value)
            log_ptr = ctypes.c_char_p(ctypes.addressof(log))
            length = ctypes.c_size_t(value.value)
            length_ptr = ctypes.byref(length)
            print(log, ctypes.byref(log),
                  ctypes.c_char_p(ctypes.addressof(log)))
            gl.glGetProgramInfoLog(self.program, length, length_ptr, log_ptr)
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
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices)*4, array,
                        gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        indices = [0, 1, 2, 0, 2, 3]
        array = (ctypes.c_ubyte * len(indices))(*indices)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(indices), array,
                        gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        # Setup texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                        self.width, self.height, 0,
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, 0)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                           gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
                           gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
                           gl.GL_CLAMP_TO_EDGE)

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

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        for line in range(height):
            # offset = self.surface.contents.pixels + (line*self.pitch)+x
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, x, y, width, 1,
                               gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
                               self.surface.contents.pixels)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def finished_framebuffer_update(self):
        """pyVNC event handler."""
        clock = time.time()

        gl.glValidateProgram(self.program)
        gl.glUseProgram(self.program)

        tex = gl.glGetUniformLocation(self.program, "texture".encode('utf-8'))
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glUniform1i(tex, 0)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 20, 0)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 20, 12)
        gl.glEnableVertexAttribArray(0)
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_BYTE, 0)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glUseProgram(0)

        sdl2.SDL_GL_SwapWindow(self.window)

        from math import ceil
        diff = time.time() - clock
        print('Frame: {:.0f}ms'.format(ceil(diff*1000)))
        print('Overhead: {:.0f}ms'.format(
            ceil((time.time() - self.clock - diff)*1000)
        ))
        print('FPS: {:.0f}'.format(1/(time.time() - self.clock)))
        self.clock = time.time()


class Sink(pyzre.ZRE):
    """Framebuffer output sink."""

    def __init__(self, loop):
        """constructor.  Requires asyncio loop."""
        pyzre.ZRE.__init__(self, loop=loop)

        self.screen = SDLRFBClient()

        self.broadcast()

    def main_loop(self):
        """update framebuffer."""
        return self.screen.update()

    def on_hello(self, peer, msg):
        """pyZRE hello event handler."""
        pass

    # ZRE event handlers
    def on_whisper(self, peer, msg):
        """pyZRE whisper event handler."""
        print(type(msg), msg)
        content = msgpack.unpackb(msg.content, encoding='utf-8')
        print(content)

        if content.get('op', None) == 'connect':
            # size = (content['width'], content['height'])

            msg = {
                'op': 'ready',
                'ip': self.ip,
                'port': self.screen.listenPort
            }

            self.whisper(peer, msgpack.packb(msg))
            self.screen.listen(-1)
        else:
            raise Exception('Unhandled msg:' + str(msg))

# TODO. Check SDL_GetNumVideoDisplays and create an instance for each
instance = Sink(asyncio.get_event_loop())

# def event_loop():
#     while True:
#         EventManager.update()
#         yield from asyncio.sleep(0)


def signal_handler(signal, frame):
    """Terminate asyncio loop on SIGINT."""
    asyncio.get_event_loop().stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def run(fn, *args):
    """run and yield as long as fn return True."""
    while fn(*args):
        yield from asyncio.sleep(0)

asyncio.get_event_loop().run_until_complete(run(instance.main_loop))
# asyncio.get_event_loop().run_forever()

sys.exit(0)
