"""Test and benchmark JPEG compression."""
import TurboJPEG
import time


def do_jpeg(data):
    """Compress data as JPEG."""
    compressor = TurboJPEG.Compress(1920, 1920, 1080, TurboJPEG.RGBA)
    start = time.time()
    compressor.compress2(data, None, 16, 90, 0)
    speed = time.time() - start
    print('{:.3f}'.format(speed))
    return


def test_speed():
    """Benchmark compression speed."""
    data = bytearray(open('/dev/urandom', 'rb').read(1920*1080*4))

    do_jpeg(data)
    data = bytearray(open('/dev/zero', 'rb').read(1920*1080*4))
    do_jpeg(data)


test_speed()
