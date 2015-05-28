Kernel Module
=============
 * Stub interface
 * Communication with userland for Rect updates and EDID
 * X11 support
 * Unload support

* Fix client startup.  Find a way to get IP before handling connections.
* Fix delay for connect method.  Client must start VNC before sending connect.
* Allow tear down of connections.  Allows client to connect/disconnect.
* Support multiple clients.

* Move away from Python?  Dealing with memory is messy.  What options are there for Pi?
* Better error handling.  We're dealing with C here.
* Cleanup/Refactor code
