cimport bcm_host as vc
from libc.stdint cimport int32_t, uint32_t, int64_t

from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.string cimport memset

DISPMANX_PROTECTION_NONE = 0

DISPMANX_NO_ROTATE = 0

# VC_IMAGE_TYPE_T:
VC_IMAGE_MIN    = 0
VC_IMAGE_RGB565 = 1
VC_IMAGE_1BPP   = 2
VC_IMAGE_YUV420 = 3
VC_IMAGE_48BPP  = 4
VC_IMAGE_RGB888 = 5


VC_IMAGE_RGBA32 = 15

VC_IMAGE_RGBX32   = 49 # 32bpp like RGBA32 but with unused alpha */ 
VC_IMAGE_RGBX8888 = 50 # 32bpp, corresponding to RGBA with unused alpha */ 
VC_IMAGE_BGRX8888 = 51 # 32bpp, corresponding to BGRA with unused alpha */ 

def bcm_host_init():
    vc.bcm_host_init()

def bcm_host_deinit():
    vc.bcm_host_deinit()

cdef class Rect:
    cdef vc.VC_RECT_T _handle

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, x, y, width, height):
        vc.vc_dispmanx_rect_set(&self._handle, x, y, width, height)

    @property
    def x(self):
        return self._handle.x

    @x.setter
    def x(self, value):
        self._handle.x = value

    @property
    def y(self):
        return self._handle.y
    @y.setter
    def y(self, value):
        self._handle.y = value

    @property
    def width(self):
        return self._handle.width
    @width.setter
    def width(self, value):
        self._handle.width = value

    @property
    def height(self):
        return self._handle.height
    @height.setter
    def height(self, value):
        self._handle.height = value

cdef class Resource:
    cdef vc.DISPMANX_RESOURCE_HANDLE_T _handle
    cdef uint32_t _image_handle

    def __cinit__(self, vc.VC_IMAGE_TYPE_T type, *args, **kwargs):
        pass

    def __init__(self, vc.VC_IMAGE_TYPE_T type, int width, int height):
        # VideoCore requires width and height to be upper 16 bits.
        width  = width  | (width  << 16)
        height = height | (height << 16)
        self._handle = vc.vc_dispmanx_resource_create(type, width, height, &self._image_handle)
        assert self._handle > 0, 'Resource create failed: ' + str(self._handle)

    def __deinit__(self):
        pass

    def __dealloc__(self):
        if self._handle > 0:
            print 'Freeing resource'
            rc = vc.vc_dispmanx_resource_delete(self._handle)
            self._handle = 0
            assert rc == 0, 'Unable to free resource' 

    def write_data(self, vc.VC_IMAGE_TYPE_T src_type, int src_pitch, unsigned char[:] src_data, Rect rect):
        cdef int rc

        # TODO: type check src_address. Must be convertible to pointer
        rc = vc.vc_dispmanx_resource_write_data(self._handle, src_type, src_pitch, &src_data[0], &rect._handle)
        assert rc == 0, 'Failed writing resource'

cdef class Display:
    cdef vc.DISPMANX_DISPLAY_HANDLE_T _handle
    cdef vc.DISPMANX_MODEINFO_T       _info

    def __cinit__(self, uint32_t screen, *args, **kwargs):
        pass

    def __init__(self, uint32_t screen, *args, **kwargs):
        cdef int rc;

        self._handle = vc.vc_dispmanx_display_open(screen);
        assert self._handle, 'Unable to open display'

        rc = vc.vc_dispmanx_display_get_info(self._handle, &self._info)
        assert rc == 0, 'Failed to get Display Info'
    
        print 'Display is %d x %d' % (self._info.width, self._info.height)

    def __dealloc__(self):
        if self._handle:
            print 'Freeing Display'
            rc = vc.vc_dispmanx_display_close(self._handle)
            self._handle = 0;
            assert rc == 0, 'Failed to close display'

    def close(self):
        cdef int rc;


cdef class Element:
    cdef vc.DISPMANX_ELEMENT_HANDLE_T _handle

    def __cinit__(self, element, *args, **kwargs):
        _handle = element

    def __dealloc__(self):
        with Update(0) as update:
            update.remove_element(self)

    def modified(self, Update update, Rect rect):
        rc = vc.vc_dispmanx_element_modified(update._handle, self._handle, &rect._handle)
        assert rc == 0, 'Element modify failed'


cdef class Update:
    cdef vc.DISPMANX_UPDATE_HANDLE_T _handle

    def __cinit__(self, *args, **kwargs):
        pass

    def __init__(self, priority):
        self._handle = vc.vc_dispmanx_update_start(priority)
        assert self._handle, 'Unable to acquire Update handle'
        # print 'Update handled acquired: ' + str(self._handle)

    def __dealloc__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.submit_sync()
        

    def add_element(self, Display display, layer, Rect dst_rect, Resource resource, Rect src_rect, protection,  transform):
        cdef vc.DISPMANX_ELEMENT_HANDLE_T element
        cdef vc.VC_DISPMANX_ALPHA_T alpha

        alpha.flags = vc.DISPMANX_FLAGS_ALPHA_FIXED_ALL_PIXELS
        alpha.opacity = 255
        alpha.mask = 0

        # VideoCore requires src width and height to be upper 16 bits.
        # TODO: Check that 0xFFFF is 0
        src_rect._handle.width  <<= 16
        src_rect._handle.height <<= 16

        # print 'Update handled acquired: ' + str(self._handle)
        element = vc.vc_dispmanx_element_add(self._handle, display._handle, layer,
            &dst_rect._handle, resource._handle, &src_rect._handle, protection,
            &alpha, NULL, transform)

        assert element > 0, 'Element failed to add'

        return Element(element)

    def remove_element(self, Element element):
        rc = vc.vc_dispmanx_element_remove( self._handle, element._handle)
        assert rc == 0, 'Error freeing element'
        print 'Element freed'

    def submit_sync(self):
        # print 'Update handled acquired: ' + str(self._handle)
        rc = vc.vc_dispmanx_update_submit_sync(self._handle)
        assert rc == 0, 'update sync failed: ' + str(rc)
