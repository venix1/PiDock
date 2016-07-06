"""Unittest for CRC32."""

# flake8: noqa: ignore=E702
import pyximport; pyximport.install()  

import pidock.crc32
import time

from pidock.crc32 import _crc32Lookup


def do_crc(data):
    """Execute CRC32 on data and time it."""
    start = time.time()
    # crc = pidock.crc32.crc32_bitwise(data, len(data))
    # crc = pidock.crc32.crc32_8bytes(data, len(data))
    crc = pidock.crc32.crc32_16bytes(data, len(data))
    speed = time.time() - start
    print('{:.3f} {:X}'.format(speed, crc))
    return crc


def test_tables():
    """Verify lookup table."""
    assert _crc32Lookup()[7][1] == 0xCCAA009E
    assert _crc32Lookup()[7][255] == 0x264B06E6


def test_empty():
    """Test CRC on empty string."""
    data = bytearray(b'')
    do_crc(data)


def test_fox():
    """Test on well known string."""
    data = bytearray(b'The quick brown fox jumped over the fence.')
    assert do_crc(data) == 0x654A380A


def test_speed():
    """Test expected use case."""
    data = bytearray(open('/dev/urandom', 'rb').read(1920*1080*4))
    do_crc(data)
    data = bytearray(open('/dev/zero', 'rb').read(1920*1080*4))
    assert do_crc(data) == 0xEB9E4E4E


test_tables()
# test_fox()
test_speed()
