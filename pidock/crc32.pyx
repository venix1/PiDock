# Based on Fast CRC32
# http://create.stephan-brumme.com/crc32/

ctypedef unsigned int u32

cdef u32 Polynomial = 0xEDB88320



# Cython can't initialize a 2D array.  Precompute
cdef u32[16][256] crc32Lookup

def _crc32Lookup():
    return crc32Lookup

def make_crc32lookup():
    cdef u32[:, :] ptr = crc32Lookup

    for i in range(256):
        crc = i
        for j in range(8):
            crc = (crc >> 1) ^ ((crc & 1) * Polynomial)
        ptr[0][i] = crc

    for i in range(256):
        # for Slicing-by-4 and Slicing-by-8
        ptr[1][i] = (ptr[0][i] >> 8) ^ ptr[0][ptr[0][i] & 0xFF];
        ptr[2][i] = (ptr[1][i] >> 8) ^ ptr[0][ptr[1][i] & 0xFF];
        ptr[3][i] = (ptr[2][i] >> 8) ^ ptr[0][ptr[2][i] & 0xFF];
        # only Slicing-by-8
        ptr[4][i] = (ptr[3][i] >> 8) ^ ptr[0][ptr[3][i] & 0xFF];
        ptr[5][i] = (ptr[4][i] >> 8) ^ ptr[0][ptr[4][i] & 0xFF];
        ptr[6][i] = (ptr[5][i] >> 8) ^ ptr[0][ptr[5][i] & 0xFF];
        ptr[7][i] = (ptr[6][i] >> 8) ^ ptr[0][ptr[6][i] & 0xFF];

        ptr[8][i] = (ptr[3][i] >> 8) ^ ptr[0][ptr[7][i] & 0xFF];
        ptr[9][i] = (ptr[4][i] >> 8) ^ ptr[0][ptr[8][i] & 0xFF];
        ptr[10][i] = (ptr[5][i] >> 8) ^ ptr[0][ptr[9][i] & 0xFF];
        ptr[11][i] = (ptr[6][i] >> 8) ^ ptr[0][ptr[10][i] & 0xFF];

        ptr[12][i] = (ptr[3][i] >> 8) ^ ptr[0][ptr[11][i] & 0xFF];
        ptr[13][i] = (ptr[4][i] >> 8) ^ ptr[0][ptr[12][i] & 0xFF];
        ptr[14][i] = (ptr[5][i] >> 8) ^ ptr[0][ptr[13][i] & 0xFF];
        ptr[15][i] = (ptr[6][i] >> 8) ^ ptr[0][ptr[14][i] & 0xFF];

make_crc32lookup()


def crc32_bitwise(unsigned char[:] ptr, u32 length, u32 p_crc32 = 0):
    cdef u32 crc = ~p_crc32
    cdef unsigned char* ch = <unsigned char*> &ptr[0]

    while length:
        length -= 1

        crc ^= ch[0]
        ch += 1

        for j in range(8):
            crc = (crc >> 1) ^ ((crc &1) * Polynomial)

    return ~crc


def crc32_8bytes(unsigned char[:] ptr, u32 length, u32 p_crc32 = 0):
    cdef u32 *current = <u32*> &ptr[0]
    cdef u32 crc = ~p_crc32
    cdef u32 one
    cdef u32 two
    cdef unsigned char *ch

    while length >= 8:
        one = current[0] ^ crc
        two = current[1]
        current += 2
        crc = crc32Lookup[7][one       & 0xFF] ^ \
              crc32Lookup[6][(one>> 8) & 0xFF] ^ \
              crc32Lookup[5][(one>>16) & 0xFF] ^ \
              crc32Lookup[4][ one>>24        ] ^ \
              crc32Lookup[3][two       & 0xFF] ^ \
              crc32Lookup[2][(two>> 8) & 0xFF] ^ \
              crc32Lookup[1][(two>>16) & 0xFF] ^ \
              crc32Lookup[0][ two>>24        ]
        length -= 8

    ch = <unsigned char*> current

    while length:
        length -= 1
        crc = (crc >> 8) ^ crc32Lookup[0][(crc & 0xFF) ^ ch[0]]
        ch += 1

    return ~crc
    
def crc32_16bytes(unsigned char[:] ptr, u32 length, u32 p_crc32 = 0):
    cdef u32 *current = <u32*> &ptr[0]
    cdef u32 crc = ~p_crc32
    cdef u32 a
    cdef u32 b
    cdef u32 c
    cdef u32 d
    cdef unsigned char *ch

    while length >= 16:
        a = current[0] ^ crc
        b = current[1]
        c = current[2]
        d = current[3]
        current += 4
        crc = crc32Lookup[15][ a      & 0xFF] ^ \
              crc32Lookup[14][(a>> 8) & 0xFF] ^ \
              crc32Lookup[13][(a>>16) & 0xFF] ^ \
              crc32Lookup[12][ a>>24        ] ^ \
              crc32Lookup[11][ b      & 0xFF] ^ \
              crc32Lookup[10][(b>> 8) & 0xFF] ^ \
              crc32Lookup[9] [(b>>16) & 0xFF] ^ \
              crc32Lookup[8] [ b>>24        ] ^ \
              crc32Lookup[7] [ c      & 0xFF] ^ \
              crc32Lookup[6] [(c>> 8) & 0xFF] ^ \
              crc32Lookup[5] [(c>>16) & 0xFF] ^ \
              crc32Lookup[4] [ c>>24        ] ^ \
              crc32Lookup[3] [ d      & 0xFF] ^ \
              crc32Lookup[2] [(d>> 8) & 0xFF] ^ \
              crc32Lookup[1] [(d>16) & 0xFF] ^ \
              crc32Lookup[0] [ d>>24        ]
        length -= 16

    ch = <unsigned char*> current

    while length:
        length -= 1
        crc = (crc >> 8) & crc32Lookup[0][(crc & 0xFF)] ^ ch[0]
        ch += 1

    return ~crc
