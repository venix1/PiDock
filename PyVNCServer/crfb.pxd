# file: crfb.pxd

cdef extern from "rfb/rfb.h":

    ctypedef bint rfbBool
    ctypedef int  rfbPixel

    cdef struct _rfbScreenInfo:
        char* frameBuffer
    ctypedef _rfbScreenInfo rfbScreenInfo
    ctypedef _rfbScreenInfo *rfbScreenInfoPtr

    # Initialization
    extern rfbScreenInfoPtr rfbGetScreen(int* argc,char** argv,
        int width,int height,int bitsPerSample,int samplesPerPixel,
        int bytesPerPixel);
    extern void rfbScreenCleanup(rfbScreenInfoPtr screenInfo)
    extern void rfbInitServer(rfbScreenInfoPtr rfbScreen);
    extern void rfbShutdownServer(rfbScreenInfoPtr rfbScreen,rfbBool disconnectClients);

    extern void rfbNewFramebuffer(rfbScreenInfoPtr rfbScreen,char *framebuffer,
        int width,int height, int bitsPerSample,int samplesPerPixel,
        int bytesPerPixel);

    # Event loop
    extern void rfbRunEventLoop(rfbScreenInfoPtr screenInfo, long usec, rfbBool runInBackground);
    extern rfbBool rfbProcessEvents(rfbScreenInfoPtr screenInfo,long usec);
    extern rfbBool rfbIsActive(rfbScreenInfoPtr screenInfo);

    # /* draw.c */
    extern void rfbFillRect(rfbScreenInfoPtr s,int x1,int y1,int x2,int y2,rfbPixel col);
    extern void rfbDrawPixel(rfbScreenInfoPtr s,int x,int y,rfbPixel col);
    extern void rfbDrawLine(rfbScreenInfoPtr s,int x1,int y1,int x2,int y2,rfbPixel col);


