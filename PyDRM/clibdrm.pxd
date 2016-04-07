cdef extern from "sys/ioctl.h":
    cdef int ioctl(int, unsigned long, ...)

cdef extern from "sys/mman.h":
    cdef void* mmap64(void*, size_t, int, int, int, unsigned long)
    cdef int MAP_FAILED
    cdef int MAP_SHARED
    cdef int PROT_READ
    cdef int PROT_WRITE

cdef extern from "libdrm/drm.h":
    ctypedef unsigned int __u32
    ctypedef unsigned long long __u64

    cdef int DRM_IOCTL_SET_MASTER
    cdef int DRM_IOCTL_MODE_GETRESOURCES
    cdef int DRM_IOCTL_MODE_GETCRTC
    cdef int DRM_IOCTL_MODE_MAP_DUMB
    cdef int DRM_IOCTL_MODE_GETFB

    cdef enum drm_map_type:
        _DRM_FRAME_BUFFER  # WC (no caching), no core dump
        _DRM_REGISTERS  # no caching, no core dump
        _DRM_SHM  # shared, cached
        _DRM_AGP  # AGP/GART
        _DRM_SCATTER_GATHER  # Scatter/gather memory for PCI DMA
        _DRM_CONSISTENT  # Consistent memory for PCI DMA
        _DRM_GEM  # GEM object

    cdef enum drm_map_flags:
        _DRM_RESTRICTED  # Cannot be mapped to user-virtual
        _DRM_READ_ONLY
        _DRM_LOCKED  # shared, cached, locked
        _DRM_KERNEL  # kernel requires access
        _DRM_WRITE_COMBINING  # use write-combining if possible
        _DRM_CONTAINS_LOCK  # SHM page that contains lock
        _DRM_REMOVABLE  # Removable mapping
        _DRM_DRIVER  # Managed by driver
    

    cdef struct drm_mode_map_dumb:
        __u32 handle
        __u32 pad
        __u64 offset

    cdef struct drm_mode_fb_cmd:
        __u32 fb_id
        __u32 width
        __u32 height
        __u32 pitch
        __u32 bpp
        __u32 depth
        __u32 handle

    cdef struct drm_mode_card_res:
        __u64 fb_id_ptr
        __u64 crtc_id_ptr
        __u64 connector_id_ptr
        __u64 encoder_id_ptr
        __u32 count_fbs
        __u32 count_crtcs
        __u32 count_connectors
        __u32 count_encoders
        __u32 min_width 
        __u32 max_width
        __u32 min_height
        __u32 max_height

    cdef struct drm_mode_crtc:
        __u64 set_connectors_ptr
        __u32 count_connectors

        __u32 crtc_id
        __u32 fb_id

        __u32 x
        __u32 y

    cdef struct drm_mode_get_connector:
        __u32 encoder_id
        __u32 connector_id
