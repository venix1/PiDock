Kernel Module
=============
 * Communication with userland for EDID
 * Allow unload/reload of module.(Crashes currently)
 * Move from netlink for mass data transfers. Options?

* Force coroutine to sleep if IP not present. Beacon code should get it soon. waits a maximum of 10 seconds.
* Add config file to specify IP and coresonding broadcast address
* Use event to send region updates to libvnc core

* Replace rpigl with pyopengl w/ gles2 support

* Support for 16 bit color with correct mapping.
* Direct Texture writing, raw transfer is 1ms, 32-bit color image xfer is 24ms.
  * EGLImage? or Search for texture data in /dev/mem
* Generate EDID from resolutionas sent by sink. Load into kernel.
* Expand pidock_nl to handle multiple messages.  Split based on attributes
* Expand pidock_nl to pass messages to kernel modules

* Fix delay for connect method.  Client must start VNC before sending connect.
* Allow tear down of connections.  Allows client to connect/disconnect.
* Smartly handle multiple CLient/Servers on same network
* Support multiple sinks.

* Have client configure sink for each valid display.
* Implement libvnc scaling?
* Get Sink EDID and pass to source. Optional.

* Improve handling of raw memory
* Better error handling.  We're dealing with C here.

* Split rendering code from logic.  Allow SDL2/OpenGL/OpenGLES/X/DirectFB clients with 
  same base
