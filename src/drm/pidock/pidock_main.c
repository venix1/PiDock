/*
 * Copyright (C) 2015 Daniel Green <venix1@gmail.com>
 * 
 * based in parts on the udl drm driver:
 * Copyright (C) 2012 Red Hat
 *
 * based in parts on udlfb.c:
 * Copyright (C) 2009 Roberto De Ioris <roberto@unbit.it>
 * Copyright (C) 2009 Jaya Kumar <jayakumar.lkml@gmail.com>
 * Copyright (C) 2009 Bernie Thompson <bernie@plugable.com>

 * This file is subject to the terms and conditions of the GNU General Public
 * License v2. See the file COPYING in the main directory of this archive for
 * more details.
 */

#include <drm/drmP.h>

#include "pidock_drv.h"

int pidock_driver_load(struct drm_device *dev, unsigned long flags)
{
	struct pidock_device *pidock;
	struct drm_vblank_crtc *vblank;
	int ret = -ENOMEM;

	DRM_DEBUG("\n");
	pidock = kzalloc(sizeof(struct pidock_device), GFP_KERNEL);
	if (!pidock)
		return -ENOMEM;

	pidock->ddev = dev;
	dev->dev_private = pidock;

	DRM_DEBUG("\n");
	ret = pidock_modeset_init(dev);
	if (ret)
		goto err;

	ret = pidock_fbdev_init(dev);
	if (ret)
		goto err;

	ret = drm_vblank_init(dev, 1);
	if (ret)
		goto err_fb;
	vblank = &dev->vblank[0];
	DRM_INFO("vblank %d", vblank->enabled);

	return 0;

err_fb:
	pidock_fbdev_cleanup(dev);
err:
	kfree(pidock);
	DRM_ERROR("%d\n", ret);
	return ret;
}

int pidock_driver_unload(struct drm_device *dev)
{
	struct pidock_device *pidock = dev->dev_private;
	struct drm_vblank_crtc *vblank;

	DRM_INFO("pidock_driver_unload:");
	vblank = &dev->vblank[0];
	DRM_INFO("vblank %d", vblank->enabled);

	drm_vblank_cleanup(dev);
	pidock_fbdev_cleanup(dev);
	pidock_modeset_cleanup(dev);
	kfree(pidock);
	return 0;
}
