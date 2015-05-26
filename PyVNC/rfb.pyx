cimport crfb
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

import ctypes


FLASH_PORT_OFFSET  = 5400
LISTEN_PORT_OFFSET = 5500
TUNNEL_PORT_OFFSET = 500
SERVER_PORT_OFFSET = 5900
DEFAULT_SSH_CMD    = "/usr/bin/ssh"



_rfbClientDict = {}
cdef registerClient(rfbClient client):
    if not client._rfbClient:
        return # or raise?

    _rfbClientDict[<size_t>client._rfbClient] = client

    # setup callbacks
    client._rfbClient.canHandleNewFBSize = True
    client._rfbClient.MallocFrameBuffer      = MallocFrameBuffer
    client._rfbClient.GotFrameBufferUpdate   = GotFrameBufferUpdate
    client._rfbClient.HandleKeyboardLedState = HandleKeyboardLedState;
    client._rfbClient.HandleTextChat         = HandleTextChat;
    client._rfbClient.GotXCutText            = GotXCutText;
    client._rfbClient.listenPort  = LISTEN_PORT_OFFSET;
    client._rfbClient.listen6Port = LISTEN_PORT_OFFSET;


cdef unregisterClient(rfbClient client):
    if not client._rfbClient:
        return # or raise?

    del _rfbClientDict[<size_t>client._rfbClient]

cdef getClientObject(size_t client):
    return _rfbClientDict.get(client, None)

cdef crfb.rfbBool MallocFrameBuffer(crfb.rfbClient* client):
    self = getClientObject(<size_t>client)
    return self.malloc_framebuffer()

cdef void GotFrameBufferUpdate(crfb.rfbClient* client, int x, int y, int w, int h):
    self = getClientObject(<size_t>client)
    self.got_framebuffer_update(x, y, w, h)

cdef void HandleKeyboardLedState(crfb.rfbClient* client, int value, int pad):
    print 'callback, keyboard'

cdef void HandleTextChat(crfb.rfbClient* client, int value, char *text):
    print 'callback, text'

cdef void GotXCutText(crfb.rfbClient* client, const char *text, int textlen):
    print 'callback, ct'

cdef class rfbClient:
    cdef crfb.rfbClient* _rfbClient

    def __cinit__(self, *args, **kwargs):
        pass

    def __dealloc__(self):
        if self._rfbClient:
            unregisterClient(self)
            crfb.rfbClientCleanup(self._rfbClient)

    def get_client(self, bitsPerSample, samplesPerPixel, bytesPerPixel):
        self._rfbClient = crfb.rfbGetClient(bitsPerSample, samplesPerPixel, bytesPerPixel)
        registerClient(self)

        cdef int argc = 1;
        cdef char* argv = "viewer";
        #if not crfb.rfbInitClient(self._rfbClient, &argc, &argv):
        #    raise Exception('unable to init client')

    @property
    def height(self):
        return self._rfbClient.height
    @property
    def width(self):
        return self._rfbClient.width

    @property
    def framebuffer(self):
        pass #return self._framebuffer

    def set_framebuffer_from_ptr(self, size_t ptr):
        cdef void* ptr = <void*>value
        self._rfbClient.frameBuffer = <unsigned char*>ptr

    @property
    def listenPort(self):
        if not self._rfbClient:
            raise Exception('Client not initialized')
        return self._rfbClient.listenPort

    def set_listenPort(self, value):
        if not self._rfbClient:
            raise Exception('Client not initialized')
        self._rfbClient.listenPort = value

        return self.listenPort

    def listen(self, timeout=-1):
        status = crfb.listenForIncomingConnectionsNoFork(self._rfbClient, timeout)
        if status == 1:
            if not crfb.rfbInitClient(self._rfbClient, NULL, NULL):
                raise Exception('unable to init client')
            return
        elif status == 0:
            raise Exception('Timeout')
        elif status == -1:
            raise Exception('Error')

    def isActive(rfbClient self):
        return self._rfbClient != NULL and self._rfbClient.sock > 0


    def WaitForMessage(self, timeout=0):
        return crfb.WaitForMessage(self._rfbClient, timeout)

    def HandleRFBServerMessage(self):
        return crfb.HandleRFBServerMessage(self._rfbClient)


_rfbScreenDict = {}
cdef registerScreen(rfbServer screen):
    if not screen._rfbScreen:
        return # or raise?

    _rfbScreenDict[<size_t>screen._rfbScreen] = screen

cdef unregisterScreen(rfbServer screen):
    if not screen._rfbScreen:
        return # or raise?

    del _rfbScreenDict[<size_t>screen._rfbScreen]

cdef class rfbClientRec:
    cdef crfb.rfbClientPtr _rfbClient

    def __cinit__(self, *args, **kwargs):
        pass

cdef class rfbServer:
    cdef crfb.rfbScreenInfoPtr _rfbScreen
    cdef char[:] _framebuffer
    cdef _clients

    def __cinit__(self, args, width, height, bitsPerSample, samplesPerPixel, bytesPerPixel, framebuffer):
        cdef int argc = 0
        cdef char** argv = NULL
        self._rfbScreen = crfb.rfbGetScreen(&argc, argv, width, height,
            bitsPerSample, samplesPerPixel, bytesPerPixel)

        size = width*height*bytesPerPixel
        cdef char* ptr
        cdef size_t address
        if framebuffer:
            address = ctypes.addressof(ctypes.c_char.from_buffer(framebuffer))
            ptr = <char*>address
            print ptr
        else:
            ptr = <char*>PyMem_Malloc(size)
        if not ptr:
            raise MemoryError()
        registerScreen(self)

        self._framebuffer = <char[:size]>ptr
        self._rfbScreen.frameBuffer = ptr;

        crfb.rfbInitServer(self._rfbScreen)


    def __dealloc__(self):
        if self._rfbScreen:
            unregisterScreen(self)
            if self._rfbScreen.frameBuffer:
                PyMem_Free(self._rfbScreen.frameBuffer)
                self._framebuffer = None

        crfb.rfbShutdownServer(self._rfbScreen, True)
        crfb.rfbScreenCleanup(self._rfbScreen)



    def __init__(self, args, width, height, bitsPerSample, samplesPerPixel, bytesPerPixel, framebuffer=None):
        self._clients = []

    def connect(self, host, port):
        assert self._rfbScreen
        if not crfb.rfbConnect(self._rfbScreen, host, port):
            raise Exception('Unable to connect to %s:%s'%(host,port))

    def reverseConnection(self, host, port):
        assert self._rfbScreen

        cdef crfb.rfbClientPtr ptr = crfb.rfbReverseConnection(self._rfbScreen, host.encode('utf-8'), port)
        if not ptr:
            raise Exception('Unable to connect to %s:%s'%(host,port))

        client = rfbClientRec()
        client._rfbClient = ptr
        self._clients.append(client)

        return client

    def fillRect(rfbServer self, p1, p2, color):
        assert self._rfbScreen and self._rfbScreen.frameBuffer
        # TODO: Bounds checking
        crfb.rfbFillRect(self._rfbScreen, p1[0], p1[1], p2[0], p2[1], color)

    def markRectAsModified(self, p1, p2):
        crfb.rfbMarkRectAsModified(self._rfbScreen, p1[0], p1[1], p2[0], p2[1])

    @property
    def framebuffer(self):
        return self._framebuffer

    def isActive(self):
        return crfb.rfbIsActive(self._rfbScreen)

    def processEvents(self, timeout=0):
        return crfb.rfbProcessEvents(self._rfbScreen, timeout)

    def runEventLoop(self):
        crfb.rfbRunEventLoop(self._rfbScreen, 4000, False)
