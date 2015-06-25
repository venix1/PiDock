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

#include <linux/module.h>
#include <linux/version.h>
#include <drm/drmP.h>

#include <drm/drm_gem_cma_helper.h>
//#include <drm/drm_crtc_helper.h>

#include "pidock_drv.h"

static int pidock_driver_set_busid(struct drm_device *d, struct drm_master *m)
{
	return 0;
}

static int pidock_enable_vblank(struct drm_device *dev, int crtc)
{
	return 0;
}

static void pidock_disable_vblank(struct drm_device *dev, int crtc)
{
}

static const struct vm_operations_struct pidock_gem_vm_ops = {
	.fault = pidock_gem_fault,
	.open = drm_gem_vm_open,
	.close = drm_gem_vm_close,
};

static const struct file_operations pidock_driver_fops = {
	.owner = THIS_MODULE,
	.open = drm_open,
	.mmap = drm_gem_mmap,
	.poll = drm_poll,
	.read = drm_read,
	.unlocked_ioctl = drm_ioctl,
	.release = drm_release,
	.llseek = noop_llseek,
};

static struct drm_driver driver = {
	.major = PIDOCK_MAJOR,
	.minor = PIDOCK_MINOR,
	.patchlevel = PIDOCK_PATCHLEVEL,

	.name = PIDOCK_NAME,
	.desc = PIDOCK_DESC,
	.date = PIDOCK_DATE,
	.driver_features = DRIVER_MODESET | DRIVER_GEM | DRIVER_PRIME,

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3, 18, 0)
    .set_busid = pidock_driver_set_busid,
#endif

	.load = pidock_driver_load,
	.unload = pidock_driver_unload,

	.gem_free_object = pidock_gem_free_object,
	.gem_vm_ops = &pidock_gem_vm_ops,

	.prime_handle_to_fd = drm_gem_prime_handle_to_fd,
	.prime_fd_to_handle = drm_gem_prime_fd_to_handle,
	//.gem_prime_import = drm_gem_prime_import,
	//.gem_prime_import_sg_table = drm_gem_cma_prime_import_sg_table,
	//.gem_prime_export = pidock_gem_prime_export,
	.gem_prime_import = pidock_gem_prime_import,

	.dumb_create = pidock_dumb_create,
	.dumb_map_offset = pidock_gem_mmap,
	.dumb_destroy = drm_gem_dumb_destroy,

	.enable_vblank = pidock_enable_vblank,
	.disable_vblank = pidock_disable_vblank,
	.get_vblank_counter = drm_vblank_count,

	.fops = &pidock_driver_fops,
};

static struct drm_device *pidock_drm;

static int __init pidock_init(void) 
{
	struct drm_device *dev;
	int err;
    printk(KERN_INFO "pidock_init:");

	err = pidock_bus_init();
	if (err)
		return err;

	dev = drm_dev_alloc(&driver, &pidock_bus);
	if (!dev)
		return -ENOMEM;

	err = drm_dev_register(dev, 0);
	if (err)
		goto err_free;

	DRM_INFO("Initialized pidock on minor %d\n", dev->primary->index);

	pidock_drm = dev;
	return 0;

err_free:
	printk(KERN_ERR "pidock_init failed");
	drm_dev_unref(dev);
	pidock_bus_cleanup();
	return err;
}

static void __exit pidock_exit(void)
{
	struct drm_device *dev = pidock_drm;

	DRM_INFO("pidock_exit: %p", pidock_drm);
	if (dev) {
		pidock_drm = NULL;
	    drm_dev_unregister(dev);
		drm_dev_unref(dev);
	}

	pidock_bus_cleanup();
}

module_init(pidock_init);
module_exit(pidock_exit);
MODULE_LICENSE("GPL");
