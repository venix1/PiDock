# file: crfb.pxd
from libc.stdint cimport uint8_t, uint16_t

ctypedef bint rfbBool
ctypedef unsigned int  rfbPixel

cdef extern from "rfb/rfbclient.h":
    ctypedef _rfbClient rfbClient
    ctypedef _rfbClient* rfbClientPtr

    ctypedef rfbBool(*MallocFrameBufferProc)(rfbClient *client);
    ctypedef void(*GotFrameBufferUpdateProc)(rfbClient *client, int x, int y, int w, int h)
    ctypedef void(*FinishedFrameBufferUpdateProc)(rfbClient *client)
    ctypedef void(*HandleKeyboardLedStateProc)(rfbClient* client, int value, int pad)
    ctypedef void(*HandleTextChatProc)(rfbClient* client, int value, char *text)
    ctypedef void(*GotXCutTextProc)(rfbClient* client, const char *text, int textlen)

    ctypedef struct rfbPixelFormat:
        uint8_t  bitsPerPixel;
        uint8_t  depth;
        uint8_t  bigEndian;
        uint8_t  trueColour;
        uint16_t redMax;
        uint16_t greenMax;
        uint16_t blueMax;
        uint8_t  redShift;
        uint8_t  greenShift;
        uint8_t  blueShift;

    ctypedef struct AppData:
        char    *encodingsString;
        int     compressLevel;
        int     qualityLevel;
        rfbBool enableJPEG;
        rfbBool useRemoteCursor;
        int     scaleSetting;

    cdef struct _rfbClient:
        AppData appData;

        rfbBool canHandleNewFBSize;
        GotFrameBufferUpdateProc GotFrameBufferUpdate;
        FinishedFrameBufferUpdateProc FinishedFrameBufferUpdate;
        MallocFrameBufferProc MallocFrameBuffer;
        HandleKeyboardLedStateProc HandleKeyboardLedState;
        HandleTextChatProc HandleTextChat;
        GotXCutTextProc GotXCutText;

        rfbPixelFormat format;
        unsigned char* frameBuffer;

        int width;
        int height;

        int sock;

        int listenSock;
        char* listenAddress;
        int listenPort;

        int listen6Sock
        char* listen6Address;
        int listen6Port


    rfbClient* rfbGetClient(int bitsPerSample, int samplesPerPixel, int bytesPerPixel);
    rfbBool rfbInitClient(rfbClient *client, int *argc, char **argv);
    void rfbClientCleanup(rfbClient* client);

    void listenForIncomingConnections(rfbClient *viewer);
    int listenForIncomingConnectionsNoFork (rfbClient *viewer, int usec_timeout);
    int ListenAtTcpPort(int port);
    int ListAtTcpPortAndAddress(int port, const char *address);

    
    int WaitForMessage(rfbClient *client, unsigned int usecs);   
    rfbBool HandleRFBServerMessage(rfbClient *client);



cdef extern from "rfb/rfb.h":

    ctypedef _rfbClientRec  rfbClientRec
    ctypedef _rfbClientRec* rfbClientPtr

    ctypedef _rfbScreenInfo rfbScreenInfo
    ctypedef _rfbScreenInfo *rfbScreenInfoPtr

    cdef struct _rfbScreenInfo:
        char* frameBuffer
        rfbBool alwaysShared;
        rfbClientPtr clientHead;
        rfbClientPtr pointerClient;  
        rfbPixelFormat serverFormat;

    cdef struct _rfbClientRec:
        pass

    # Initialization
    rfbScreenInfoPtr rfbGetScreen(int* argc,char** argv,
        int width,int height,int bitsPerSample,int samplesPerPixel,
        int bytesPerPixel);
    void rfbScreenCleanup(rfbScreenInfoPtr screenInfo)
    void rfbInitServer(rfbScreenInfoPtr rfbScreen);
    void rfbShutdownServer(rfbScreenInfoPtr rfbScreen,rfbBool disconnectClients);

    int rfbConnect(rfbScreenInfoPtr rfbScreen, char *host, int port);
    rfbClientPtr rfbReverseConnection(rfbScreenInfoPtr rfbScreen, char *host, int port);

    void rfbNewFramebuffer(rfbScreenInfoPtr rfbScreen,char *framebuffer,
        int width,int height, int bitsPerSample,int samplesPerPixel,
        int bytesPerPixel);

    # Event loop
    void rfbRunEventLoop(rfbScreenInfoPtr screenInfo, long usec, rfbBool runInBackground);
    rfbBool rfbProcessEvents(rfbScreenInfoPtr screenInfo,long usec);
    rfbBool rfbIsActive(rfbScreenInfoPtr screenInfo);

    # /* draw.c */
    void rfbMarkRectAsModified( rfbScreenInfoPtr rfbScreen, int x1, int y1, int x2, int y2);
    void rfbFillRect(rfbScreenInfoPtr s,int x1,int y1,int x2,int y2,rfbPixel col);
    void rfbDrawPixel(rfbScreenInfoPtr s,int x,int y,rfbPixel col);
    void rfbDrawLine(rfbScreenInfoPtr s,int x1,int y1,int x2,int y2,rfbPixel col);



