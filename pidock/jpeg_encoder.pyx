from cpython cimport array
import array
import pidock.crc32
import time
from pidock.crc32 import crc32_16bytes

BLOCK_SIZE=64

ctypedef unsigned int uint

cdef class Region:
    cdef uint x1, y1
    cdef uint x2, y2

    def __init__(self, uint x1, uint y1, uint x2, uint y2):
        self.x1 = x1
        self.y1 = y1

        self.x2 = x2
        self.y2 = y2

        assert self.width > 0, 'x1 not < x2'
        assert self.height > 0, 'y1 not < y2'

    property x:
        def __get__(self):
            return self.x1
        def __set__(self, value):
            self.x1 = value

    property y:
        def __get__(self):
            return self.y1
        def __set__(self, value):
            self.y1 = value

    property height:
        def __get__(self):
            return self.y2 - self.y1
        def __set__(self, value):
            self.y2 = self.y1 + value

    property width:
        def __get__(self):
            return self.x2 - self.x1
        def __set__(self, value):
            self.x2 = self.x1 + value

cdef unsigned int round(n, d):
    return (n + d // 2) // d

cdef class CRC32Blocks:
    cdef array.array _crc32_python
    cdef bitmap
    cdef uint[:] _crc32
    cdef uint _height
    cdef uint _width
    cdef uint block_size

    def __init__(self, width, height, block_size=BLOCK_SIZE):
        self.block_size = block_size
        self.bitmap = set()

        self._width = width // block_size
        self._height = height  // block_size

        self._crc32_python = array.array('I', [0] * self._width * self._height)
        self._crc32 = self._crc32_python

    def __getitem__(self, uint idx):
        return self._crc32[idx]

    def __setitem__(self, uint idx, uint value):
        self._crc32[idx] = value

    def mark_region(self, region):
        x = region.x // self.block_size
        y = region.y // self.block_size
        w = region.width // self.block_size
        h = region.height // self.block_size
        print(region, x, y, w, h)
        print(self._width, self._height)

        start = y * self._width + x
        for i in range(h):
            for j in range(w):
                self.bitmap.add(start)
                start += 1
            start += self._width - w


cdef class JPEGEncoder:
    cdef uint height, width
    cdef CRC32Blocks crc32
    cdef unsigned char[:] _fb
    cdef changed 

    def __init__(self, args, width, height, bitsPerSample, samplesPerPixel,
    bytesPerPixel, unsigned char[:] framebuffer):
        self.changed = set()
        self._fb = framebuffer
        self.resize(width, height)
        
    cdef resize(self, width, height):
        self.crc32 = CRC32Blocks(width, height)
        self.height = height
        self.width = width

    @property
    def is_active(self):
        return True

    def process_events(self, timeout=0):
        cdef unsigned int p = 0
        cdef unsigned int block
        cdef unsigned int crc32
        self.changed.clear()
        start = time.time()
        for block in self.crc32.bitmap:
            crc32 = 0
            p = block * 64
            for i in range(64):
                crc32 = crc32_16bytes(self._fb[p:], 64, crc32)
                p += self.width
            if crc32 == self.crc32[block]:
                continue
            self.crc32[block] = crc32

            self.changed.add(block)
            print(self.changed)
        print('{:.6f}'.format(time.time() - start))

    def mark_rect_as_modified(self, x1, y1, x2, y2):
        if x2 == 0:
            x2 = 1
        cdef r = Region(x1, y1, x2, y2)
        print(x1, y1, x2, y2)

        self.crc32.mark_region(r)
