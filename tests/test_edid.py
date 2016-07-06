"""Test EDID class"""
import pytest

# flake8: noqa

from pidock.edid import EDID, DetailedTimingDescriptor, MonitorSerialDescriptor, MonitorNameDescriptor, MonitorRangeDescriptor

def color_identity(color):
    edid = EDID()
    setattr(edid, color, (0.35, 0.329))
    assert getattr(edid, color + '_x') == 0.35, getattr(edid, color + '_x')
    assert getattr(edid, color + '_y') == 0.329, getattr(edid, color + '_y')
    assert getattr(edid, color) == (0.35, 0.329), getattr(edid, color)

def color_range(color):
    edid = EDID()

    setattr(edid, color, (0,0))
    setattr(edid, color+'_x', 0)
    setattr(edid, color+'_y', 0)

    with pytest.raises(ValueError):
        setattr(edid, color+'_x', -1)
    with pytest.raises(ValueError):
        setattr(edid, color+'_x', 1)
    with pytest.raises(ValueError):
        setattr(edid, color+'_y', -1)
    with pytest.raises(ValueError):
        setattr(edid, color+'_y', 1)
    with pytest.raises(ValueError):
        setattr(edid, color, (0, -1))
    with pytest.raises(ValueError):
        setattr(edid, color, (0, 1))
    with pytest.raises(ValueError):
        setattr(edid, color, (-1, 0))
    with pytest.raises(ValueError):
        setattr(edid, color, (1, 0))

def test_chroma():
    for color in ['red', 'blue', 'green', 'white']:
        yield color_identity, color
        yield color_range, color

def test_DetailedTimingDescriptor():
    desc = DetailedTimingDescriptor()

    for value in [-1, 0, 660]:
        with pytest.raises(ValueError):
            desc.pixel_clock = value
    desc.pixel_clock = 620.2121
    assert desc.pixel_clock == 620.21, desc.pixel_clock

    for attr in ['hactive', 'hblank', 'vactive', 'vblank']:
        for value in [-1, 0, 4096]:
            print('Testing',attr,value)
            with pytest.raises(ValueError):
                setattr(desc, attr, value)
        setattr(desc, attr, 1024)
        assert getattr(desc, attr) == 1024, getattr(desc, attr)

    for attr in ['hsyncoffset', 'hsyncwidth']:
        setattr(desc, attr, 1024)
        assert getattr(desc, attr) == 1024, getattr(desc, attr)

    for attr in ['vsyncoffset', 'vsyncwidth']:
        setattr(desc, attr, 1024)
        assert getattr(desc, attr) == 1024, getattr(desc, attr)

    desc.display_size = (1024,1024)
    assert desc.display_size == (1024,1024), desc.display_size
    desc.display_width = 66
    assert desc.display_width == 66, desc.display_width
    desc.display_height = 77
    assert desc.display_height == 77, desc.display_height

    for attr in ['hborder', 'vborder']:
        # for value in [-1, 0, 4096]:
        #     print('Testing',attr,value)
        #     with pytest.raises(ValueError):
        #         setattr(desc, attr, value)
        setattr(desc, attr, 128)
        assert getattr(desc, attr) == 128, getattr(desc, attr)

    assert desc.hborder == 128, desc.hborder
    assert desc.vborder == 128, desc.vborder

def test_MonitorRangeDescriptor():
    desc = MonitorRangeDescriptor((1, 12), (1, 12), 220)
    assert desc.vmin == 1

def test_MonitorNameDescriptor():
    desc = MonitorNameDescriptor('0123456789ABC')
    assert desc.name == '0123456789ABC', desc.serial
    desc.name = '012345'
    assert desc.name == '012345', desc.serial

def test_MonitorSerialDescriptor():
    desc = MonitorSerialDescriptor('0123456789ABC')
    assert desc.serial == '0123456789ABC', desc.serial
    desc.serial = '012345'
    assert desc.serial == '012345', desc.serial

