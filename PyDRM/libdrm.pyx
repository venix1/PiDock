cimport clibdrm
import os

from clibdrm cimport __u32, __u64, mmap64
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.string cimport memset
from libc.errno cimport errno


cdef class DRMCard:
    cdef clibdrm.drm_mode_card_res drm_resources
    cdef crtcs
    cdef fd
    cdef fp

    def __cinit__(self, *args, **kwargs):
        pass

    def __dealloc__(self):  
        pass

    def __init__(self, card):
        self.fp = open(card, 'r+b')

        # probably not
        # clibdrm.ioctl(self.fd, clibdrm.DRM_IOCTL_SET_MASTER, 0)

        self.crtcs = []

    cdef cleanup(self):
        if self.drm_resources.connector_id_ptr:
            PyMem_Free(<void*>self.drm_resources.connector_id_ptr)

        if self.drm_resources.crtc_id_ptr:
            PyMem_Free(<void*>self.drm_resources.crtc_id_ptr)

        if self.drm_resources.encoder_id_ptr:
            PyMem_Free(<void*>self.drm_resources.encoder_id_ptr)

        if self.drm_resources.fb_id_ptr:
            PyMem_Free(<void*>self.drm_resources.fb_id_ptr)

        memset(&self.drm_resources, 0, sizeof(self.drm_resources))
        

    def refresh(self):
        self.cleanup()
        
        status = clibdrm.ioctl(self.fd,
                               clibdrm.DRM_IOCTL_MODE_GETRESOURCES,
                               &self.drm_resources)

        assert status == 0, status

        if self.drm_resources.count_connectors:
            size = self.drm_resources.count_connectors * sizeof(__u64)
            self.drm_resources.connector_id_ptr = <__u64> PyMem_Malloc(size)
            memset(<void*>self.drm_resources.connector_id_ptr, 0, size)

        if self.drm_resources.count_crtcs:
            size = self.drm_resources.count_crtcs * sizeof(__u64)
            self.drm_resources.crtc_id_ptr = <__u64> PyMem_Malloc(size)
            memset(<void*>self.drm_resources.crtc_id_ptr, 0, size)

        if self.drm_resources.count_encoders:
            size = self.drm_resources.count_encoders * sizeof(__u64)
            self.drm_resources.encoder_id_ptr = <__u64> PyMem_Malloc(size)
            memset(<void*>self.drm_resources.encoder_id_ptr, 0, size)

        if self.drm_resources.count_fbs:
            size = self.drm_resources.count_fbs * sizeof(__u64)
            self.drm_resources.fb_id_ptr = <__u64> PyMem_Malloc(size)
            memset(<void*>self.drm_resources.fb_id_ptr, 0, size)

        status = clibdrm.ioctl(self.fd,
                               clibdrm.DRM_IOCTL_MODE_GETRESOURCES,
                               &self.drm_resources)
        assert status == 0, status

        cdef __u64* crtc_ids = <__u64*>self.drm_resources.crtc_id_ptr
        for i in range(self.drm_resources.count_crtcs):
            self.get_crtc(crtc_ids[i])
            # self.crtcs.append(DRMCRTC(self, crtc_ids[i]))
            # print(i, crtc_ids[i])

    @property
    def fd(self):
        return self.fp.fileno()

    @property
    def count_encoders(self):
        return self.drm_resources.count_encoders

    @property
    def count_fbs(self):
        return self.drm_resources.count_fbs

    @property
    def count_connectors(self):
        return self.drm_resources.count_connectors

    @property
    def count_crtcs(self):
        return self.drm_resources.count_crtcs

    def get_connector(self, connector_id):
        cdef clibdrm.drm_mode_get_connector r
        memset(&r, 0, sizeof(r))

        r.connector_id = connector_id

    def get_crtc(self, crtc_id):
        cdef clibdrm.drm_mode_crtc r
        memset(&r, 0, sizeof(r))

        r.crtc_id = crtc_id

        clibdrm.ioctl(self.fd, clibdrm.DRM_IOCTL_MODE_GETCRTC, &r)

        return DRMCRTC(self, r)

    def get_fb(self, fb_id):
        cdef clibdrm.drm_mode_fb_cmd r
        memset(&r, 0, sizeof(r))

        r.fb_id = fb_id

        if clibdrm.ioctl(self.fd, clibdrm.DRM_IOCTL_MODE_GETFB, &r):
            raise Exception('errno: {} {}'.format(errno, os.strerror(errno)))

        return r

    def map_dumb(self, handle):
        cdef clibdrm.drm_mode_map_dumb r
        memset(&r, 0, sizeof(r))

        r.handle = handle

        if clibdrm.ioctl(self.fd, clibdrm.DRM_IOCTL_MODE_MAP_DUMB, &r):
            raise Exception('errno: {} {}'.format(errno, os.strerror(errno)))

        return r

    def mmap64(self, size, offset):
        cdef unsigned char[:] mm
        cdef void* ptr

        ptr = mmap64(<void*>0, size, 
                     clibdrm.PROT_READ | clibdrm.PROT_WRITE,
                     clibdrm.MAP_SHARED, self.fd, offset)
        if ptr == <void*> clibdrm.MAP_FAILED:
            raise Exception('errno: {} {}'.format(errno, os.strerror(errno)))
        
        print(<unsigned long>ptr)

        mm = <unsigned char[:size]> ptr
        return mm

cdef class DRMCRTC:
    def __init__(self, drm, crtc_id):
        print(crtc_id)

cdef class DRMFrameBuffer:
    cdef clibdrm.drm_mode_fb_cmd r

    def __init__(self, drm, fb_id):
        self.drm = drm


class DRMMap(object):
    def __init__(self):
        self.map = None

    def mmap(self):
        if self.map:
            return self.map

        # self.map = mmap(0, sel
