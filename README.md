Opensource Docking station using a raspberry PI over ethernet.

xrandr output sink
USB-IP
http://tigervnc.org 
https://www.kernel.org/doc/htmldocs/drm/index.html
http://1984.lsi.us.es/~pablo/docs/spae.pdf
http://people.freedesktop.org/~marcheu/linuxgraphicsdrivers.pdf
http://www.linuxjournal.com/article/2476

Concept
-------

Requires kernel DRM module (with fbdev emulation? I want a console).  Userland
daemon connects via netlink socket. Driver must support xrandr 1.4 and function
as an output sink.

Pluggable Encoder/Decoder
 * Allow OpenCL encoders using GPU
 * Multi-threaded encoding/decoding

JPEG GPU
 * http://developer.amd.com/resources/documentation-articles/articles-whitepapers/jpeg-decoding-with-run-length-encoding-a-cpu-and-gpu-approach/
 * http://www.fastcompression.com/products/jpeg/cuda-jpeg.htm
 * https://software.intel.com/en-us/articles/opencl-drivers
 *  https://www.altera.com/support/support-resources/design-examples/design-software/opencl/jpeg-decoder.html
 * https://github.com/kk1fff/jpeg-opencl
 * https://sourceforge.net/projects/gpujpeg/
 * http://developer.amd.com/tools-and-sdks/opencl-zone/amd-accelerated-parallel-processing-app-sdk/
 * http://www.cse.cuhk.edu.hk/~ttwong/demo/dwtgpu/dwtgpu.html#gpudwt

Userland software(python?) is responsible for
 * Client discovery using 0mq/ZRE.
   Discovery: http://rfc.zeromq.org/spec:20/ZRE
   http://rfc.zeromq.org/spec:26/CURVEZMQ : http://curvezmq.org/
   Authentication: http://rfc.zeromq.org/spec:27
   Authorized Keys: Using 6 Digit verification code on first connection.(Chromecast)
 * Encoding framebuffer using libvncserver.  COmmunication with drm driver using libnl
 * Eventually. Using USB-IP to pass USB data acting as a USB hub
 ? Can we multiplex screens on as single port? May need tunnel?.  Sink listens.
 ? Encryption preferred but not required.

Allow for DisplayPort GPIO adapter.  Allowing 1 PI to power multiple displays.  Ideally, this piece of 
hardware takes raw FB via memory mapped I/O and does the rest. Bandwidth may be an issue.

Optional middleman for network screens.

Network Protocol.(MsgPack)
--------------------------
* Sink emits Beacon
* Source receives Beacon.  Connects to Mailbox.
* Sink accepts connection, or refuses(in-use)
* Sink sends EDID, VNC port, and authentication information to Source.
* Source connects to Sink using libVNCServer.
* Source authenticates over VNC(Backchannel)
* Possible VNC Heartbeat extension to maintain connection.

Video Transfer Protocol
-----------------------
* Updates only
* Encoder/Decoder
* JPEG encoding frames

VNC setup from server to client.
--------------------------------
Sink(PiDock) uses ZRE to announce it's presence.  Source will establish
connection and authenticate. If the sink is already handling another session
it should reject the connection with an error code. 

After authentication sink will configure a reverse VNC port along with some 
means of verifying the Source connected.  Backchannel? Require public-key 
crypto.

The Sink will then provide the equivalent of an EDID to the Source for output
configuration.  The source will pick an output format and then connect to the 
opened port.  

Optional? The sink should stop broadcasting it's Beacon as long as the
Source is connected.


Milestones
----------


