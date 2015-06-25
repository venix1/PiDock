# file: bcm_host.pxd
# https://github.com/raspberrypi/firmware/blob/master/opt/vc/src/hello_pi/hello_dispmanx/dispmanx.c

from libc.stdint cimport int32_t, uint32_t, int64_t

DISPMANX_PROTECTION_NONE = 0;

cdef extern from "bcm_host.h":
    void bcm_host_init();
    void bcm_Host_deinit()

    # vc_image_types.h
    ctypedef enum VC_IMAGE_TYPE_T:
        VC_IMAGE_MIN = 0,
        VC_IMAGE_RGB565 = 1,
        VC_IMAGE_1BPP,
        VC_IMAGE_YUV420,
        VC_IMAGE_48BPP,
        VC_IMAGE_RGB888,
        # ...



    struct tag_VC_RECT_T:
        int32_t x;
        int32_t y;
        int32_t width;
        int32_t height;
    ctypedef tag_VC_RECT_T VC_RECT_T;

    # vc_dispmanx_types.h


    # Opaque handles
    ctypedef uint32_t DISPMANX_DISPLAY_HANDLE_T;
    ctypedef uint32_t DISPMANX_UPDATE_HANDLE_T;
    ctypedef uint32_t DISPMANX_ELEMENT_HANDLE_T;
    ctypedef uint32_t DISPMANX_RESOURCE_HANDLE_T;

    ctypedef uint32_t DISPMANX_PROTECTION_T;


    ctypedef int32_t  VCHI_MEM_HANDLE_T;

    ctypedef enum DISPMANX_TRANSFORM_T:
        DISPMANX_NO_ROTATE = 0,

    ctypedef enum DISPMANX_FLAGS_ALPHA_T:
        DISPMANX_FLAGS_ALPHA_FROM_SOURCE = 0,
        DISPMANX_FLAGS_ALPHA_FIXED_ALL_PIXELS = 1

    ctypedef struct VC_DISPMANX_ALPHA_T:
        DISPMANX_FLAGS_ALPHA_T flags;
        uint32_t opacity;
        DISPMANX_RESOURCE_HANDLE_T mask;

    ctypedef struct DISPMANX_CLAMP_T:
        # DISPMANX_FLAGS_CLAMP_T mode;
        # DISPMANX_FLAGS_KEYMASK_T key_mask;
        # DISPMANX_CLAMP_KEYS_T key_value;
        uint32_t replace_value;

    ctypedef struct DISPMANX_MODEINFO_T:
        int32_t width;
        int32_t height;
        # DISPMANX_TRANSFORM_T transform;
        # DISPLAY_INPUT_FORMAT_T input_format;
        uint32_t display_num;


    # from "vc_dispmanx.h"

    int vc_dispmanx_rect_set( VC_RECT_T *rect, uint32_t x_offset, uint32_t y_offset, uint32_t width, uint32_t height );

    # Resourcesa
    DISPMANX_RESOURCE_HANDLE_T vc_dispmanx_resource_create( VC_IMAGE_TYPE_T type, uint32_t width, uint32_t height, uint32_t *native_image_handle );
    int vc_dispmanx_resource_write_data( DISPMANX_RESOURCE_HANDLE_T res, VC_IMAGE_TYPE_T src_type, int src_pitch, void * src_address, const VC_RECT_T * rect );
    int vc_dispmanx_resource_write_data_handle( DISPMANX_RESOURCE_HANDLE_T res, VC_IMAGE_TYPE_T src_type, int src_pitch, VCHI_MEM_HANDLE_T handle, uint32_t offset, const VC_RECT_T * rect );
    int vc_dispmanx_resource_delete( DISPMANX_RESOURCE_HANDLE_T res );

    # Displays

    # Opens a display on the given device
    DISPMANX_DISPLAY_HANDLE_T vc_dispmanx_display_open( uint32_t device );

    # get the width, height, frame rate and aspect ratio of the display
    int vc_dispmanx_display_get_info( DISPMANX_DISPLAY_HANDLE_T display, DISPMANX_MODEINFO_T * pinfo );

    int vc_dispmanx_display_close( DISPMANX_DISPLAY_HANDLE_T display);

    # Updates
    DISPMANX_UPDATE_HANDLE_T vc_dispmanx_update_start( int32_t priority );
    
    # Add an element to display as part of an update
    DISPMANX_ELEMENT_HANDLE_T vc_dispmanx_element_add ( DISPMANX_UPDATE_HANDLE_T update, 
        DISPMANX_DISPLAY_HANDLE_T display, int32_t layer, const VC_RECT_T *dest_rect, 
        DISPMANX_RESOURCE_HANDLE_T src, const VC_RECT_T *src_rect, DISPMANX_PROTECTION_T protection, 
        VC_DISPMANX_ALPHA_T *alpha, DISPMANX_CLAMP_T *clamp, DISPMANX_TRANSFORM_T transform );

    int vc_dispmanx_element_modified( DISPMANX_UPDATE_HANDLE_T, DISPMANX_ELEMENT_HANDLE_T, const VC_RECT_T*)

    int vc_dispmanx_element_remove( DISPMANX_UPDATE_HANDLE_T update, DISPMANX_ELEMENT_HANDLE_T element);

    # End an update and wait for it to complete
    int vc_dispmanx_update_submit_sync( DISPMANX_UPDATE_HANDLE_T update );
    
