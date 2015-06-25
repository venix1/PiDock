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
// #include <linux/slab.h>
// #include <linux/fb.h>
// #include <linux/dma-buf.h>

#include <drm/drmP.h>
// #include <drm/drm_crtc.h>
#include <drm/drm_crtc_helper.h>
#include "pidock_drv.h"

#include <drm/drm_fb_helper.h>

static int fb_bpp = 24;

module_param(fb_bpp, int, S_IWUSR | S_IRUSR | S_IWGRP | S_IRGRP);

struct pidock_fbdev {
	struct drm_fb_helper helper;
	struct pidock_framebuffer pfb;
	struct list_head fbdev_list;
	int fb_count;
};

static int pidock_fb_mmap(struct fb_info *info, struct vm_area_struct *vma)
{
	unsigned long start = vma->vm_start;
	unsigned long size = vma->vm_end - vma->vm_start;
	unsigned long offset = vma->vm_pgoff << PAGE_SHIFT;
	unsigned long page, pos;

	DRM_INFO("pidock_fb_mmap:");

	DRM_INFO("%d + %d > %d", offset, size, info->fix.smem_len);
	if (offset + size > info->fix.smem_len)
		return -EINVAL;

	pos = (unsigned long)info->fix.smem_start + offset;

	DRM_INFO("mmap() framebuffer addr:%lu size:%lu\n",
		pos, size);

	while (size > 0) {
		page = vmalloc_to_pfn((void *)pos);
		if (remap_pfn_range(vma, start, page, PAGE_SIZE, PAGE_SHARED))
			return -EAGAIN;

		start += PAGE_SIZE;
		pos += PAGE_SIZE;
		if (size > PAGE_SIZE)
			size -= PAGE_SIZE;
		else
			size = 0;
	}

	return 0;
}

static void pidock_fb_fillrect(struct fb_info *info, const struct fb_fillrect *rect)
{
	struct pidock_fbdev *pfbdev = info->par;

	sys_fillrect(info, rect);

	pidock_nl_handle_damage(&pfbdev->pfb,
		rect->dx, rect->dy, 
		rect->width, rect->height);
}

static void pidock_fb_copyarea(struct fb_info *info, const struct fb_copyarea *region)
{
	struct pidock_fbdev *pfbdev = info->par;

	sys_copyarea(info, region);

	pidock_nl_handle_damage(&pfbdev->pfb,
		region->dx, region->dy, 
		region->width, region->height);
}

static void pidock_fb_imageblit(struct fb_info *info, const struct fb_image *image)
{
	struct pidock_fbdev *pfbdev = info->par;

	sys_imageblit(info, image);

	pidock_nl_handle_damage(&pfbdev->pfb,
		image->dx, image->dy, 
		image->width, image->height);
}


/*
 * It's common for several clients to have framebuffer open simultaneously.
 * e.g. both fbcon and X. Makes things interesting.
 * Assumes caller is holding info->lock (for open and release at least)
 */
static int pidock_fb_open(struct fb_info *info, int user)
{
	struct pidock_fbdev *pfbdev = info->par;
	// struct drm_device *dev = pfbdev->pfb.base.dev;
	// struct pidock_device *pidock = dev->dev_private;

	/* TODO: Fail is userland daemon is gone */

	pfbdev->fb_count++;

	pr_notice("open /dev/fb%d user=%d fb_info=%p count=%d\n",
		info->node, user, info, pfbdev->fb_count);

	return 0;
}


/*
 * Assumes caller is holding info->lock mutex (for open and release at least)
 */
static int pidock_fb_release(struct fb_info *info, int user)
{
	struct pidock_fbdev *pfbdev = info->par;

	pfbdev->fb_count--;

	pr_warn("released /dev/fb%d user=%d count=%d\n",
		info->node, user, pfbdev->fb_count);

	return 0;
}

int pidock_fb_check_var(struct fb_var_screeninfo *var,
                            struct fb_info *info)
{
        struct drm_fb_helper *fb_helper = info->par;
        struct drm_framebuffer *fb = fb_helper->fb;
        int depth;

		DRM_INFO("pidock_fb_check_var");

        if (var->pixclock != 0 || in_dbg_master())
                return -EINVAL;

        /* Need to resize the fb object !!! */
        if (var->bits_per_pixel > fb->bits_per_pixel ||
            var->xres > fb->width || var->yres > fb->height ||
            var->xres_virtual > fb->width || var->yres_virtual > fb->height) {
                DRM_INFO("fb userspace requested width/height/bpp is greater than current fb "
                          "request %dx%d-%d (virtual %dx%d) > %dx%d-%d\n",
                          var->xres, var->yres, var->bits_per_pixel,
                          var->xres_virtual, var->yres_virtual,
                          fb->width, fb->height, fb->bits_per_pixel);
                return -EINVAL;
        }

        switch (var->bits_per_pixel) {
        case 16:
                depth = (var->green.length == 6) ? 16 : 15;
                break;
        case 32:
                depth = (var->transp.length > 0) ? 32 : 24;
                break;
        default:
                depth = var->bits_per_pixel;
                break;
        }

        switch (depth) {
        case 8:
                var->red.offset = 0;
                var->green.offset = 0;
                var->blue.offset = 0;
                var->red.length = 8;
                var->green.length = 8;
                var->blue.length = 8;
                var->transp.length = 0;
                var->transp.offset = 0;
                break;
        case 15:
                var->red.offset = 10;
                var->green.offset = 5;
                var->blue.offset = 0;
                var->red.length = 5;
                var->green.length = 5;
                var->blue.length = 5;
                var->transp.length = 1;
                var->transp.offset = 15;
                break;
        case 16:
                var->red.offset = 11;
                var->green.offset = 5;
                var->blue.offset = 0;
                var->red.length = 5;
                var->green.length = 6;
                var->blue.length = 5;
                var->transp.length = 0;
                var->transp.offset = 0;
                break;
        case 24:
                var->red.offset = 16;
                var->green.offset = 8;
                var->blue.offset = 0;
                var->red.length = 8;
                var->green.length = 8;
                var->blue.length = 8;
                var->transp.length = 0;
                var->transp.offset = 0;
                break;
        case 32:
                var->red.offset = 16;
                var->green.offset = 8;
                var->blue.offset = 0;
                var->red.length = 8;
                var->green.length = 8;
                var->blue.length = 8;
                var->transp.length = 8;
                var->transp.offset = 24;
                break;
        default:
			DRM_INFO("pidock_fb_check_var!!!");
                return -EINVAL;
        }
		DRM_INFO("pidock_fb_check_var: exit");
        return 0;
}


static struct fb_ops pidockfb_ops = {
	.owner = THIS_MODULE,
	.fb_check_var = pidock_fb_check_var,
	.fb_set_par = drm_fb_helper_set_par,
	.fb_fillrect = pidock_fb_fillrect,
	.fb_copyarea = pidock_fb_copyarea,
	.fb_imageblit = pidock_fb_imageblit,
	.fb_pan_display = drm_fb_helper_pan_display,
	.fb_blank = drm_fb_helper_blank,
	.fb_setcmap = drm_fb_helper_setcmap,
	.fb_debug_enter = drm_fb_helper_debug_enter,
	.fb_debug_leave = drm_fb_helper_debug_leave,
	.fb_mmap = pidock_fb_mmap,
	.fb_open = pidock_fb_open,
	.fb_release = pidock_fb_release,
};

static int pidock_user_framebuffer_dirty(
	struct drm_framebuffer *fb,
	struct drm_file *file,
	unsigned flags, unsigned color,
	struct drm_clip_rect *clips,
	unsigned num_clips)
{
	struct pidock_framebuffer *pfb = to_pidock_fb(fb);
	int i;
	int ret = 0;
	DRM_INFO("pidock_user_framebuffer_dirty: pfb:%p", pfb);

	drm_modeset_lock_all(fb->dev);

	if (!pfb->active)
		goto unlock;

	for (i = 0; i < num_clips; i++) {
		DRM_INFO("    pidock_user_framebuffer_dirty: (%d, %d) - (%d, %d)",
			clips[i].x1, clips[i].y1,
			clips[i].x2, clips[i].y2);
			//pidock_nl_handle_damage(pfb, 0, 0, pfb->base.width, pfb->base.height);
		ret = pidock_nl_handle_damage(pfb,
				clips[i].x1, clips[i].y1,
				clips[i].x2 - clips[i].x1,
				clips[i].y2 - clips[i].y1);
		if (ret)
			break;
	}


unlock:
	drm_modeset_unlock_all(fb->dev);

	return ret;
}

static void pidock_user_framebuffer_destroy(struct drm_framebuffer *fb)
{
	struct pidock_framebuffer *pfb = to_pidock_fb(fb);

	DRM_INFO("pidock_user_framebuffer_destroy: pfb:%p", pfb);

	if (pfb->obj)
		drm_gem_object_unreference_unlocked(&pfb->obj->base);

	drm_framebuffer_cleanup(fb);
	kfree(pfb);
}

static const struct drm_framebuffer_funcs pidockfb_funcs = {
	.destroy = pidock_user_framebuffer_destroy,
	.dirty = pidock_user_framebuffer_dirty,
};

static int
pidock_framebuffer_init(
	struct drm_device *dev,
	struct pidock_framebuffer *pfb,
	struct drm_mode_fb_cmd2 *mode_cmd,
	struct pidock_gem_object *obj)
{
	int ret;
	DRM_INFO("pidock_framebuffer_init:");

	spin_lock_init(&pfb->dirty_lock);
	pfb->obj = obj;
	drm_helper_mode_fill_fb_struct(&pfb->base, mode_cmd);
	ret = drm_framebuffer_init(dev, &pfb->base, &pidockfb_funcs);
	DRM_INFO("    pfb:%p", pfb);
	return ret;
}

static int pidockfb_create(
	struct drm_fb_helper *helper,
	struct drm_fb_helper_surface_size *sizes)
{
	struct pidock_fbdev *pfbdev =
		container_of(helper, struct pidock_fbdev, helper);
	struct drm_device *dev = pfbdev->helper.dev;
	struct fb_info *info;
	struct device *device = dev->dev;
	struct drm_framebuffer *fb;
	struct drm_mode_fb_cmd2 mode_cmd;
	struct pidock_gem_object *obj;
	uint32_t size;
	int ret = 0;

	DRM_INFO("pidockfb_create: %dx%d", sizes->surface_width, sizes->surface_height);
	
	if (sizes->surface_bpp == 24)
		sizes->surface_bpp = 32;

	mode_cmd.width = sizes->surface_width;
	mode_cmd.height = sizes->surface_height;
	mode_cmd.pitches[0] = mode_cmd.width * ((sizes->surface_bpp + 7) / 8);

	mode_cmd.pixel_format = drm_mode_legacy_fb_format(
		sizes->surface_bpp,
		sizes->surface_depth);

	size = mode_cmd.pitches[0] * mode_cmd.height;
	size = ALIGN(size, PAGE_SIZE);

	obj = pidock_gem_alloc_object(dev, size);
	if (!obj)
		goto out;

	ret = pidock_gem_vmap(obj);
	if (ret) {
		DRM_ERROR("failed to vmap fb\n");
		goto out_gfree;
	}

	info = framebuffer_alloc(0, device);
	if (!info) {
		ret = -ENOMEM;
		goto out_gfree;
	}
	info->par = pfbdev;

	ret = pidock_framebuffer_init(dev, &pfbdev->pfb, &mode_cmd, obj);
	if (ret)
		goto out_gfree;
	
	fb = &pfbdev->pfb.base;

	pfbdev->helper.fb = fb;
	pfbdev->helper.fbdev = info;

	strcpy(info->fix.id, "pidockdrmfb");

	info->screen_base = pfbdev->pfb.obj->vmapping;
	info->fix.smem_len = size;
	info->fix.smem_start = (unsigned long)pfbdev->pfb.obj->vmapping;

	info->flags = FBINFO_DEFAULT | FBINFO_CAN_FORCE_OUTPUT;
	info->fbops = &pidockfb_ops;
	drm_fb_helper_fill_fix(info, fb->pitches[0], fb->depth);
	drm_fb_helper_fill_var(info, &pfbdev->helper, sizes->fb_width, sizes->fb_height);

	ret = fb_alloc_cmap(&info->cmap, 256, 0);
	if (ret) {
		ret = -ENOMEM;
		goto out_gfree;
	}

	DRM_DEBUG_KMS("allocated %dx%d vmal %p\n",
		fb->width, fb->height,
		pfbdev->pfb.obj->vmapping);

	DRM_INFO("pidockfb_create: return %d", ret);
	return ret;
out_gfree:
	drm_gem_object_unreference(&pfbdev->pfb.obj->base);
out:
	return ret;
}

static const struct drm_fb_helper_funcs pidock_fb_helper_funcs = {
	.fb_probe = pidockfb_create,
};

static void pidock_fbdev_destroy(struct drm_device *dev,
	struct pidock_fbdev *pfbdev)
{
	struct fb_info *info;
	DRM_INFO("pidock_fbdev_destroy");
	if (pfbdev->helper.fbdev) {
		info = pfbdev->helper.fbdev;
		unregister_framebuffer(info);
		if (info->cmap.len)
			fb_dealloc_cmap(&info->cmap);
		framebuffer_release(info);
	}
	drm_fb_helper_fini(&pfbdev->helper);
	drm_framebuffer_unregister_private(&pfbdev->pfb.base);
	drm_framebuffer_cleanup(&pfbdev->pfb.base);
	drm_gem_object_unreference_unlocked(&pfbdev->pfb.obj->base);
}


int pidock_fbdev_init(struct drm_device *dev)
{
	struct pidock_device *pidock = dev->dev_private;
	int bpp_sel = fb_bpp;
	struct pidock_fbdev *pfbdev;
	int ret;

	DRM_INFO("pidock_fbdev_init:");

	pfbdev = kzalloc(sizeof(struct pidock_fbdev), GFP_KERNEL);
	if (!pfbdev)
		return -ENOMEM;

	pidock->fbdev = pfbdev;

	drm_fb_helper_prepare(dev, &pfbdev->helper, &pidock_fb_helper_funcs);
	
	ret = drm_fb_helper_init(dev, &pfbdev->helper, 1, 1);
	if (ret)
		goto free;

	ret = drm_fb_helper_single_add_all_connectors(&pfbdev->helper);
	if (ret)
		goto fini;

	drm_helper_disable_unused_functions(dev);

	ret = drm_fb_helper_initial_config(&pfbdev->helper, bpp_sel);
	if (ret)
		goto fini;

	DRM_INFO("pidock_fbdev_init: exit - %d", ret);
	return 0;

fini:
	drm_fb_helper_fini(&pfbdev->helper);
free:
	kfree(pfbdev);
	DRM_INFO("pidock_fbdev_init: exit - %d", ret);
	return ret;
}

void pidock_fbdev_cleanup(struct drm_device *dev)
{
	struct pidock_device *pidock = dev->dev_private;
	DRM_INFO("pidock_fbdev_cleanup");
	if (!pidock->fbdev)
		return;

	pidock_fbdev_destroy(dev, pidock->fbdev);
	kfree(pidock->fbdev);
	pidock->fbdev = NULL;
}

struct drm_framebuffer *
pidock_fb_user_fb_create(struct drm_device *dev,
                   struct drm_file *file,
                   struct drm_mode_fb_cmd2 *mode_cmd)
{
	struct drm_gem_object *obj;
	struct pidock_framebuffer *pfb;
	int ret;
	uint32_t size;

	DRM_INFO("pidock_fb_user_fb_create: %.4s %d %d", (char *)&mode_cmd->pixel_format, mode_cmd->pitches[0], mode_cmd->height);

	obj = drm_gem_object_lookup(dev, file, mode_cmd->handles[0]);
	if (obj == NULL)
		return ERR_PTR(-ENOENT);

	size = mode_cmd->pitches[0] * mode_cmd->height;
	size = ALIGN(size, PAGE_SIZE);

	if (size > obj->size) {
		DRM_ERROR("object size not sufficient for fb %d %zu %d %d\n", size, obj->size, mode_cmd->pitches[0], mode_cmd->height);
		return ERR_PTR(-ENOMEM);
	}

	pfb = kzalloc(sizeof(*pfb), GFP_KERNEL);
	if (pfb == NULL)
		return ERR_PTR(-ENOMEM);

	ret = pidock_framebuffer_init(dev, pfb, mode_cmd, to_pidock_bo(obj));
	if (ret) {
		kfree(pfb);
		return ERR_PTR(-EINVAL);
	}
	DRM_INFO("pidock_fb_user_fb_create: exit 0");
	return &pfb->base;
}
