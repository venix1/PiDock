* Unitests for Benchmarks
* LibDRM.Net
* class TileEncoder
* class ZRE
* class ITransport
* class EDID
* Port Crc32C.Net for linux

* replace RFB class
* Wrap libjpeg api
* Generate CRC32 blocks
* Checksum on update
* Encoder Plugin
* Transport layer

* Unittests as benchmarks
 * test crc32 encoding speed
 * test jpeg encoding speed

* Configuration file. 
  * Contains Broadcast IP/Port
  * Indicates VNC should listen on
  * Encryption configuration

* Automatic framebuffer identification
  * Get DRMCard from netlink
  * Get Framebuffer from netlink
  * Clean up DRM class for simpler mmap


* Encoder Plugins
  * Types
    * Autoswitch based on efficiencies
	* Fullscreen updates use h264
	* Partial updates use jpeg
    * JPEG Type
	* H264 Type
	* Other?
  * Marked regions are double checked with CRC32.
  * Any failed blocks are jpeg converted and transmitted
  * Replace RFB class
    * framebuffer configuration
	* Connection active(ZMQ broadcast?)
	* Register change.
	* Update Framebuffer changes.
  * JPEG encoder/decoder class
    * Blackbox overlay
	* Allows switch to shader
	* libjpegturbo default
  * Wire format.
    General: CMD:u8, SIZE:u16, DATA[]
	TILE len(jpeg) jpeg_rect

* Research YUV encoding(Same some CPU cycles)

* [DONE] Sink: Get Display modes from SDL. 
* [DONE] Sink: Send display modes to source.
* Sink: Grabs current EDID from OS
* [DONE] Sink: build EDID from display modes

* Source: Tell kernel about connection
* Kernel: Add Connector in disconnected state.

* Kernel: Create netlink message for receiving EDID
* Source: Send EDID to kernel
* Kernel: Load EDID into connector. Set connected

* MMAP framebuffer for VNC.

* Kernel: Refactor crtc/connector for dynamic allocation
  * CRTC per Display
  * Encoder per CRTC
  * Connector per Encoder
* Kernel: pidock_crtc dynamically created, with encoder, connector
  See pidock_modeset_init for framework

* Source: Wait for display events
* Kernel: Add netlink message for display events(encoder?)
* Kernel: Monitor and report display events.
* Kernel: On display change, send via Netlink
* Source: On display activation, send selected display to sink.
* Sink: Set SDL display mode, configure VNC.

* Source: Add Netlink message indicating display change.
* Kernel: Export framebuffer via mmap.
* Kernel: Netlink messages indicating FB change.

* Source/Sink: Allow tear down of connections.  

* Source/Sink: Support multiple VNC connections in a single instance.
* Source/Sink: libvnc scaling


* Improve handshake when IP is not know.
  * Force coroutine to sleep if IP not present. 
  * Beacon code should recieve it's own IP.
  * Wait for 10 seconds.

* Have source convert to RGBA encoding
* Determine source framebuffer encoding.  Pass to sink.

* Use event to send region updates to libvnc core

* Security keys. For encrypted communication.

* Fix delay for connect method.  Client must start VNC before sending connect.
* Smartly handle multiple CLient/Servers on same network
* Support multiple sinks. TCP port conflict. 

* Improve handling of raw memory
* Better error handling.  We're dealing with C here.

* Replace rpigl with pyopengl w/ gles2 support

* Support for 16 bit color with correct mapping.

* Raspberry PI optimizations
  * JPEG hardware decoder
  * Direct texture writes. memcpy is 24ms for 32-bit 1080p
    * EGLImage
	* Search /dev/mem

* Extendable transport mechanism. ie: ZRE, Central Server, Direct

* Split rendering code from logic.  Allow SDL2/OpenGL/OpenGLES/X/DirectFB clients with 
  same base
