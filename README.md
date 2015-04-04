Opensource Docking station using a raspberry PI over ethernet.

xrandr output sink
USB-IP
http://tigervnc.org 
https://www.kernel.org/doc/htmldocs/drm/index.html

Concept
-------

Requires kernel DRM module with fbdev support.  Userland daemon connects via netlink socket. Driver
must support xrandr 1.4 and function as an output sink.

Userland software(python?) is responsible for
 * Client discovery using 0mq.
   http://rfc.zeromq.org/spec:26/CURVEZMQ : http://curvezmq.org/
   Discovery: http://rfc.zeromq.org/spec:20/ZRE
   Authentication: http://rfc.zeromq.org/spec:27
   Authorized Keys: Using 6 Digit verification code on first connection.(Chromecast)
 * Encoding framebuffer using libvncserver.  COmmunication with drm driver using libnl
 ? Using USB-IP to pass USB data acting as a USB hub
 ? Encryption preferred but not required.

Allow for DisplayPort GPIO adapter.  Allowing 1 PI to power multiple displays.  Ideally, this piece of 
hardware takes raw FB via memory mapped I/O and does the rest. Bandwidth may be an issue.


