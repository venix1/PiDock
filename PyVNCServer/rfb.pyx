cimport crfb
from libc.stdlib cimport malloc,free

cdef class Server:
    cdef crfb.rfbScreenInfoPtr _rfbScreen

    def __cinit__(self, args, width, height, bitsPerSample, samplesPerPixel, bytesPerPixel):
        cdef int argc = 0
        cdef char** argv = NULL
        self._rfbScreen = crfb.rfbGetScreen(&argc, argv, width, height,
            bitsPerSample, samplesPerPixel, bytesPerPixel)
        self._rfbScreen.frameBuffer=<char*>malloc(width*height*bytesPerPixel)
        crfb.rfbInitServer(self._rfbScreen)

    def __dealloc__(self):
        if self._rfbScreen.frameBuffer is not NULL:
            free(self._rfbScreen.frameBuffer)
        crfb.rfbShutdownServer(self._rfbScreen, True)
        crfb.rfbScreenCleanup(self._rfbScreen)


    def __init__(self, args, width, height, bitsPerSample, samplesPerPixel, bytesPerPixel):
        pass

    def runEventLoop(self):
        crfb.rfbRunEventLoop(self._rfbScreen, 4000, False)
