"""Test DRM module support."""

import libdrm

drm = libdrm.DRMCard('/dev/dri/card1')

drm.refresh()
# print(drm.count_connectors)
# print(drm.count_crtcs)
# print(drm.count_fbs)
# print(drm.count_encoders)

r = drm.get_fb(23)
print(r)
size = r['height'] * r['pitch']

r = drm.map_dumb(1)
print(r)

fb = drm.mmap64(size, r['offset'])
print(fb)

with open('snapshot.data', 'wb') as fp:
    fp.write(fb)
