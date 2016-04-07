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

struct pidock_device *pidock_dev;

int pidock_driver_load(struct drm_device *dev, unsigned long flags)
{
	struct pidock_device *pidock;
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

	ret = pidock_output_init(dev);
	if (ret)
		goto err;

	ret = pidock_fbdev_init(dev);
	if (ret)
		goto err;

	ret = drm_vblank_init(dev, 1);
	if (ret)
		goto err_fb;

	ret = pidock_nl_init(pidock);
	if (ret)
		goto err_fb;

	pidock_dev = pidock;
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
	int i;

	DRM_INFO("pidock_driver_unload:");

	pidock_nl_cleanup(pidock);
	drm_vblank_cleanup(dev);
	pidock_fbdev_cleanup(dev);
	for(i=0; i<PIDOCK_MAX_OUTPUT; ++i) {
		if (pidock->output[i])
			pidock_output_cleanup(dev, pidock->output[i]);
			pidock->output[i] = NULL;
	}
	pidock_modeset_cleanup(dev);
	kfree(pidock);
	return 0;
}
