"""Python module for representing EDID and related structures."""

from ctypes import Structure, Union, c_ubyte, c_ushort, sizeof
from fractions import Fraction

# Established timings lookup table.
# (width, height, frequency)
EST_TIMINGS = [
    # Byte 35, Bits 0-7
    (800, 600, 60),
    (800, 600, 56),
    (640, 480, 75),
    (640, 480, 72),
    (640, 480, 67),
    (640, 480, 60),
    (720, 400, 88),
    (720, 400, 70),

    # Byte 36, Bits 0-7
    (1280, 1024, 75),
    (1024, 768, 75),
    (1024, 768, 72),
    (1024, 768, 60),
    (1024, 768, 87),
    (832, 624, 75),
    (800, 600, 75),
    (800, 600, 72),

    # Byte 37, bits 0-7
    # bits 0-6, Other?
    # bit 7, (1152,870,75)
]


class EstTiming(Structure):
    """Python representation of EDID Established Timing."""

    _pack_ = True
    _fields_ = [
        ('modes', c_ubyte * 3),
    ]


class StdTiming(Structure):
    """Python reprensentation of EDID Standard Timing."""

    _pack_ = True
    _fields_ = [
        ('width', c_ubyte),
        ('frequency', c_ubyte, 4),
        ('ratio', c_ubyte, 4),
    ]


class DetailedTimingDescriptor(Structure):
    """Python representation of EDID Detailed TIming Descriptor."""

    _pack_ = True
    _fields_ = [
        ('pclk', c_ushort),
        ('hactive_0', c_ubyte),
        ('hblank_0', c_ubyte),
        ('hblank_1', c_ubyte, 4),
        ('hactive_1', c_ubyte, 4),

        ('vactive_0', c_ubyte),
        ('vblank_0', c_ubyte),
        ('vblank_1', c_ubyte, 4),
        ('vactive_1', c_ubyte, 4),

        ('hsyncoffset_0', c_ubyte),
        ('hsynctime_0', c_ubyte),

        ('vsyncwidth_0', c_ubyte, 4),
        ('vsyncoffset_0', c_ubyte, 4),

        ('vsyncwidth_1', c_ubyte, 2),
        ('vsyncoffset_1', c_ubyte, 2),
        ('hsyncwidth_1', c_ubyte, 2),
        ('hsyncoffset_1', c_ubyte, 2),

        ('display_width_0', c_ubyte),
        ('display_height_0', c_ubyte),
        ('display_height_1', c_ubyte, 4),
        ('display_width_1', c_ubyte, 4),
        ('hborder_0', c_ubyte),
        ('vborder_0', c_ubyte),
        ('features', c_ubyte)
    ]

    def __init__(self):
        """constructor."""
        # width
        # height
        # hborder
        # vborder
        # features
        pass

    @staticmethod
    def from_modeline(modeline):
        """Generate detailed timing from modeline string."""
        pass

    @property
    def pixel_clock(self):
        """Return pixel clock."""
        return self.pclk/100

    @pixel_clock.setter
    def pixel_clock(self, value):
        """Set pixel clock."""
        if value <= 0:
            raise ValueError('Pixel clock too low')
        if value > 655.35:
            raise ValueError('Pixel clock too high')
        self.pclk = int(value * 100)

    @property
    def hactive(self):
        """Return horizontal active pixels."""
        return self.hactive_0 + (self.hactive_1 << 8)

    @hactive.setter
    def hactive(self, value):
        """Set horizontal active pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.hactive_0 = value & 0xFF
        self.hactive_1 = (value & 0xF00) >> 8

    @property
    def hblank(self):
        """Return horizontal blank in pixels."""
        return self.hblank_0 + (self.hblank_1 << 8)

    @hblank.setter
    def hblank(self, value):
        """Set horizontal blank in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.hblank_0 = value & 0xFF
        self.hblank_1 = (value & 0xF00) >> 8

    @property
    def vactive(self):
        """Return active vertical area in pixels."""
        return self.vactive_0 + (self.vactive_1 << 8)

    @vactive.setter
    def vactive(self, value):
        """Set active vertical area in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.vactive_0 = value & 0xFF
        self.vactive_1 = (value & 0xF00) >> 8

    @property
    def vblank(self):
        """Return vertical blank in pixels."""
        return self.vblank_0 + (self.vblank_1 << 8)

    @vblank.setter
    def vblank(self, value):
        """Set vertical blank in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.vblank_0 = value & 0xFF
        self.vblank_1 = (value & 0xF00) >> 8

    @property
    def hsync_offset(self):
        """Return horizontal sync offset in pixels."""
        return self.hsyncoffset_0 + (self.hsyncoffset_1 << 8)

    @hsync_offset.setter
    def hsync_offset(self, value):
        """Set horizontal sync offset in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.hsyncoffset_0 = value & 0xFF
        self.hsyncoffset_1 = (value & 0xF00) >> 8

    @property
    def hsync_width(self):
        """Return horizonal sync width in pixels."""
        return self.hsyncwidth_0 + (self.hsyncwidth_1 << 8)

    @hsync_width.setter
    def hsync_width(self, value):
        """Set horizontal sync width in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.hsyncwidth_0 = value & 0xFF
        self.hsyncwidth_1 = (value & 0xF00) >> 8

    @property
    def vsync_offset(self):
        """Return vertical offset in pixels."""
        return self.vsyncoffset_0 + (self.vsyncoffset_1 << 8)

    @vsync_offset.setter
    def vsync_offset(self, value):
        """Set vertical offset in pixels."""
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.vsyncoffset_0 = value & 0xFF
        self.vsyncoffset_1 = (value & 0xF00) >> 8

    @property
    def vsync_width(self):
        """Return vertical sync width in pixels."""
        return self.vsyncwidth_0 + (self.vsyncwidth_1 << 8)

    @vsync_width.setter
    def vsync_width(self, value):
        """Set vertical sync width in pixels."""
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.vsyncwidth_0 = value & 0xFF
        self.vsyncwidth_1 = (value & 0xF00) >> 8

    @property
    def display_size(self):
        """Return display width and height in pixels."""
        return (self.display_width, self.display_height)

    @display_size.setter
    def display_size(self, value):
        """Set display width and height in pixels."""
        self.display_width = value[0]
        self.display_height = value[1]

    @property
    def display_width(self):
        """Return display width in pixels."""
        return self.display_width_0 + (self.display_width_1 << 8)

    @display_width.setter
    def display_width(self, value):
        """Set display width in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.display_width_0 = value & 0xFF
        self.display_width_1 = (value & 0xF00) >> 8

    @property
    def display_height(self):
        """Return display height in pixels."""
        return self.display_height_0 + (self.display_height_1 << 8)

    @display_height.setter
    def display_height(self, value):
        """Set display height in pixels."""
        if value <= 0:
            raise ValueError('Value must be greater than 0')
        if value >= 4096:
            raise ValueError('Value is not less than 4096')
        self.display_height_0 = value & 0xFF
        self.display_height_1 = (value & 0xF00) >> 8

    @property
    def hborder(self):
        """Return horizontal border."""
        return self.hborder_0

    @hborder.setter
    def hborder(self, value):
        """Return horizontal border."""
        self.hborder_0 = value

    @property
    def vborder(self):
        """Return vertical border."""
        return self.vborder_0

    @vborder.setter
    def vborder(self, value):
        """Set vertical border."""
        self.vborder_0 = value

    def __str__():
        """Generate modeline for text output."""


class MonitorRangeDescriptor(Structure):
    """Python representation of EDID Monitor Range Descriptor."""

    _pack_ = True
    _fields_ = [
        ('header', c_ubyte * 5),
        ('vmin', c_ubyte),
        ('vmax', c_ubyte),
        ('hmin', c_ubyte),
        ('hmax', c_ubyte),
        ('clockmax', c_ubyte),
        ('gtf', c_ubyte * 8)
    ]

    def __init__(self, vertical, horizontal, clock):
        """Initialize Range descriptor."""
        self.header = (c_ubyte * 5)(0, 0, 0, 0xFD, 0)
        self.vmin = vertical[0]
        self.vmax = vertical[1]

        self.hmin = horizontal[0]
        self.hmax = horizontal[1]

        self.clockmax = clock


class MonitorNameDescriptor(Structure):
    """Python representation of EDID Monitor Name Descriptor."""

    _pack_ = True
    _fields_ = [
        ('header', c_ubyte * 5),
        ('name0', c_ubyte * 13)
    ]

    def __init__(self, name):
        """Initailize descriptor based on name."""
        self.header = (c_ubyte * 5)(0, 0, 0, 0xFC, 0)
        self.name = name

    @property
    def name(self):
        """Return monitor name."""
        return bytearray(self.name0).decode('utf-8').split('\n')[0]

    @name.setter
    def name(self, value):
        """Set monitor name."""
        assert len(value) <= 13, 'name too long'
        name = value.encode('utf-8')
        for i in range(13):
            if i < len(name):
                self.name0[i] = name[i]
            elif i == len(name):
                self.name0[i] = 0x0A
            else:
                self.name0[i] = 0x20


class MonitorSerialDescriptor(Structure):
    """Python representation of EDID Serial Descriptor."""

    _pack_ = True
    _fields_ = [
        ('header', c_ubyte * 5),
        ('serial0', c_ubyte * 13)
    ]

    def __init__(self, serial):
        """Initialize descriptor based on serial string."""
        self.header = (c_ubyte * 5)(0, 0, 0, 0xFF, 0)
        self.serial = serial

    @property
    def serial(self):
        """Return EDID Serial string."""
        return bytearray(self.serial0).decode('utf-8').split('\n')[0]

    @serial.setter
    def serial(self, value):
        """Set EDID Serial string."""
        assert len(value) <= 13, 'serial too long'
        serial = value.encode('utf-8')
        for i in range(13):
            if i < len(serial):
                self.serial0[i] = serial[i]
            elif i == len(serial):
                self.serial0[i] = 0x0A
            else:
                self.serial0[i] = 0x20


class Descriptor(Union):
    """Generic EDID Descriptor."""

    _pack_ = True
    _fields_ = [
        ('raw', c_ubyte * 18),
        ('detailed_timing', DetailedTimingDescriptor),
        ('monitor_range', MonitorRangeDescriptor),
        ('monitor_name', MonitorNameDescriptor),
        ('monitor_serial', MonitorSerialDescriptor),
    ]

assert sizeof(Descriptor) == 18, 'All descripts are not 18 bytes in size'
assert sizeof(DetailedTimingDescriptor) == 18, \
    'Detailed Timing Descriptor not 18 bytes'
assert sizeof(MonitorRangeDescriptor) == 18, \
    'Monitor Range Descriptor not 18 bytes'
assert sizeof(MonitorNameDescriptor) == 18, \
    'Monitor Name Descriptor not 18 bytes'
assert sizeof(MonitorSerialDescriptor) == 18, \
    'Monitor Serial Descriptor not 18 bytes'


class EDID(Structure):
    """EDID structure."""

    _pack_ = True
    _fields_ = [
        ('header',   c_ubyte * 8),
        ('vendor',   c_ubyte * 2),
        ('product',  c_ubyte * 2),
        ('serial',   c_ubyte * 4),
        ('week',     c_ubyte),
        ('year',     c_ubyte),
        ('version',  c_ubyte),
        ('revision', c_ubyte),

        ('input', c_ubyte),
        ('width_cm', c_ubyte),
        ('height_cm', c_ubyte),
        ('gamma', c_ubyte),
        ('features', c_ubyte),

        # Chromaticity coordinates
        ('red_x_0', c_ubyte, 2),
        ('red_y_0', c_ubyte, 2),
        ('green_x_0', c_ubyte, 2),
        ('green_y_0', c_ubyte, 2),

        ('blue_x_0', c_ubyte, 2),
        ('blue_y_0', c_ubyte, 2),
        ('white_x_0', c_ubyte, 2),
        ('white_y_0', c_ubyte, 2),

        ('red_x_1', c_ubyte),
        ('red_y_1', c_ubyte),
        ('green_x_1', c_ubyte),
        ('green_y_1', c_ubyte),
        ('blue_x_1', c_ubyte),
        ('blue_y_1', c_ubyte),
        ('white_x_1', c_ubyte),
        ('white_y_1', c_ubyte),

        # Timing modes
        ('est', EstTiming),
        ('std', StdTiming * 8),

        ('descriptor', Descriptor * 4),
        ('extensions', c_ubyte),
        ('checksum', c_ubyte),
    ]

    def __init__(self):
        """Populate an empty EDID structure."""
        self.header = (c_ubyte * 8)(0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0)
        self.version = 1
        self.revision = 3

        # Options which could be overwritten
        # Set vendor
        # Set product
        # Set serial
        # set week
        # set year

        # Default Customization
        # ('input', c_ubyte),
        # ('width_cm', c_ubyte),
        # ('height_cm', c_ubyte),
        # ('gamma', c_ubyte),
        # ('features', c_ubyte),

        # Chromaticity coordinates

        # ('red_green_lo', c_ubyte),
        # ('blue_white_lo', c_ubyte),
        # ('red', c_ubyte * 2),
        # ('green', c_ubyte * 2),
        # ('blue', c_ubyte * 2),
        # ('white', c_ubyte * 2),

        # Set all Std. Timings to Unused
        for i in range(len(self.std)):
            self.std[i].width = 1
            self.std[i].frequency = 1

        self.std_count = 0

    def __get_chroma(color):
        pass

    def __set_chroma(color, value):
        pass

    # Red attributes
    @property
    def red(self):
        """Return red X and Y parameters."""
        return (self.red_x, self.red_y)

    @red.setter
    def red(self, value):
        """Set red X and Y parameters."""
        self.red_x = value[0]
        self.red_y = value[1]

    @property
    def red_x(self):
        """Return red X parameter."""
        return round((self.red_x_0 + (self.red_x_1 << 2))/1024, 3)

    @red_x.setter
    def red_x(self, value):
        """Set red X parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.red_x_0 = value & 0x3
        self.red_x_1 = (value & 0x3FC) >> 2

    @property
    def red_y(self):
        """Return red Y parameter."""
        return round((self.red_y_0 + (self.red_y_1 << 2))/1024, 3)

    @red_y.setter
    def red_y(self, value):
        """Set red Y parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.red_y_0 = value & 0x3
        self.red_y_1 = (value & 0x3FC) >> 2

    # Blue attributes
    @property
    def blue(self):
        """Return blue X and Y parameters."""
        return (self.blue_x, self.blue_y)

    @blue.setter
    def blue(self, value):
        """Set blue X and Y parameters."""
        self.blue_x = value[0]
        self.blue_y = value[1]

    @property
    def blue_x(self):
        """Return blue X parameter."""
        return round((self.blue_x_0 + (self.blue_x_1 << 2))/1024, 3)

    @blue_x.setter
    def blue_x(self, value):
        """Set blue X parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        assert value >= 0 and value < 1024, 'Value out of range'
        self.blue_x_0 = value & 0x3
        self.blue_x_1 = (value & 0x3FC) >> 2

    @property
    def blue_y(self):
        """Return blue Y parameter."""
        return round((self.blue_y_0 + (self.blue_y_1 << 2))/1024, 3)

    @blue_y.setter
    def blue_y(self, value):
        """Set blue Y parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.blue_y_0 = value & 0x3
        self.blue_y_1 = (value & 0x3FC) >> 2

    # Green attributes
    @property
    def green(self):
        """Return green X and Y parameters."""
        return (self.green_x, self.green_y)

    @green.setter
    def green(self, value):
        """Set green X and Y parameters."""
        self.green_x = value[0]
        self.green_y = value[1]

    @property
    def green_x(self):
        """Return green X parameter."""
        return round((self.green_x_0 + (self.green_x_1 << 2))/1024, 3)

    @green_x.setter
    def green_x(self, value):
        """Set green X parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.green_x_0 = value & 0x3
        self.green_x_1 = (value & 0x3FC) >> 2

    @property
    def green_y(self):
        """Return green y parameter."""
        return round((self.green_y_0 + (self.green_y_1 << 2))/1024, 3)

    @green_y.setter
    def green_y(self, value):
        """Set green Y parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.green_y_0 = value & 0x3
        self.green_y_1 = (value & 0x3FC) >> 2

    @property
    def white(self):
        """Return white X and Y parameters."""
        return (self.white_x, self.white_y)

    @white.setter
    def white(self, value):
        """Set white X and Y parameters."""
        self.white_x = value[0]
        self.white_y = value[1]

    @property
    def white_x(self):
        """Return white X parameter."""
        return round((self.white_x_0 + (self.white_x_1 << 2))/1024, 3)

    @white_x.setter
    def white_x(self, value):
        """Set white X parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.white_x_0 = value & 0x3
        self.white_x_1 = (value & 0x3FC) >> 2

    @property
    def white_y(self):
        """Return White Y parameter."""
        return round((self.white_y_0 + (self.white_y_1 << 2))/1024, 3)

    @white_y.setter
    def white_y(self, value):
        """Set white Y parameter."""
        value = round(value * 1024)
        if value < 0 or value > 1023:
            raise ValueError('Value must be [0, 1.0)')
        self.white_y_0 = value & 0x3
        self.white_y_1 = (value & 0x3FC) >> 2

    def add_std_timing(self, width, height, frequency):
        """Add Standard timing."""
        aspect = Fraction(width, height)
        if str(aspect) == '16/9':
            ratio = 0b11
        elif str(aspect) == '16/10':
            ratio = 0b10
        elif str(aspect) == '4/3':
            ratio = 0b01
        elif str(aspect) == '5/4':
            ratio = 0b10
        else:
            # Cannot be set as std timing
            raise Exception('Invalid aspect ratio')

        std = StdTiming()
        std.width = int(width/8)
        std.ratio = ratio
        std.frequency = frequency
        self.std[self.std_count] = std
        self.std_count += 1

    def add_modeline(self, mode):
        """Convert modeline to descriptor."""
        mode = mode.split(' ')
        # pclk = int(float(mode[1])*100)
        hdisp = int(mode[2])
        hsyncstart = int(mode[3])
        # hsyncend = int(mode[4])
        htotal = int(mode[5])

        vdisp = int(mode[6])
        vsyncstart = int(mode[7])
        # vsyncend = int(mode[8])
        vtotal = int(mode[9])

        # print(pclk)
        # print(hdisp, hsyncstart, hsyncend, htotal)
        # print(vdisp, vsyncstart, vsyncend, vtotal)
        # for i in range(10,len(mode)):
        #     print(mode[i])

        desc = DetailedTimingDescriptor()
        desc.hactive = hdisp
        desc.hblank = htotal - hdisp
        desc.hsync_offset = hsyncstart - hdisp
        desc.hsync_time = htotal - hdisp

        desc.vactive = vdisp
        desc.vblank = vtotal - vdisp
        desc.vsync_offset = vsyncstart - vdisp
        desc.vsync_time = vtotal - vdisp

        self.descriptor[0].detailed_timing = desc

    def add_descriptor(self, desc):
        """Add descriptor."""
        for i in range(len(self.descriptor)):
            if not self.descriptor[i].raw[:5] == [0, 0, 0, 0, 0]:
                continue

            for field in self.descriptor._type_._fields_:
                if isinstance(desc, field[1]):
                    setattr(self.descriptor[i], field[0], desc)
            break

    def add_mode(self, width, height, frequency):
        """Add timing for width, height, and frequency."""
        print('add_mode: {}x{}@{}'.format(width, height, frequency))
        # Is established mode?
        try:
            index = EST_TIMINGS.index((width, height, frequency))
            self.est[index] = 1
            return
        except ValueError:
            pass

        # Can this be stored as a standard timing?
        if width < 2288 and self.std_count < 8:
            try:
                return self.add_std_timing(width, height, frequency)
            except:
                pass

        return self.add_detailed_timing(width, height, frequency)

    def calculate_checksum(self):
        """Generate EDID checksum."""
        self.checksum = (256 - sum(bytearray(self)[:-1]) % 256)

    def asBytes(self):
        """Convert EDID structure to bytearray."""
        self.calculate_checksum()
        return bytearray(self)[:]

assert sizeof(EDID) == 128, 'EDID structure not 128 bytes'
