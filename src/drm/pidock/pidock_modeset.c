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
#include <drm/drm_crtc.h>
#include <drm/drm_crtc_helper.h>
 #include <drm/drm_plane_helper.h>
#include "pidock_drv.h"

static int pidock_vidreg_lock(void)
{
	/* TODO: stub */
	DRM_INFO("pidock_vidreg_lock: stub");
	return 0;
}

static int pidock_vidreg_unlock(void)
{
	/* TODO: stub */
	DRM_INFO("pidock_vidreg_unlock: stub");
	return 0;
}

static int pidock_set_blank(int dpms_mode)
{
	switch (dpms_mode) {
		case DRM_MODE_DPMS_OFF:
			break;
		case DRM_MODE_DPMS_STANDBY:
			break;
		case DRM_MODE_DPMS_SUSPEND:
			break;
		case DRM_MODE_DPMS_ON:
			break;
	}

	/* TODO: stub */
	DRM_INFO("pidock_set_blank: stub");
	return 0;
}

static int pidock_set_color_depth(u8 selection)
{
	/* TODO: stub */
	DRM_INFO("pidock_set_color_depth: stub");
	return 0;
}

static int pidock_crtc_write_mode_to_hw(struct drm_crtc *crtc)
{
	//struct drm_device *dev = crtc->dev;
	//struct pidock_device *pidock = dev->dev_private;
	int retval=0;

	/* TODO: stub */
	DRM_INFO("pidock_crtc_write_mode_to_hw: stub");

	return retval;
}

static void pidock_crtc_dpms(struct drm_crtc *crtc, int mode)
{
	struct drm_device *dev = crtc->dev;
	struct pidock_device *pidock = dev->dev_private;

	DRM_INFO("pidock_crtc_dpms: enter");
	if (mode == DRM_MODE_DPMS_OFF) {
		/* TODO: stub */
		DRM_INFO("pidock_crtc_dpms: off");
	} else {
		if (pidock->mode_buf_len == 0) {
			DRM_ERROR("Trying to enable DPMS with no mode\n");
			return;
		}	
		DRM_INFO("pidock_crtc_dpms: on");
		pidock_crtc_write_mode_to_hw(crtc);
	}
}

static bool pidock_crtc_mode_fixup(struct drm_crtc *crtc,
	const struct drm_display_mode *mode,
	struct drm_display_mode *adjusted_mode)
{        
	DRM_INFO("pidock_crtc_mode_fixup:");
	return true;
}

static int pidock_crtc_mode_set(struct drm_crtc *crtc,
                               struct drm_display_mode *mode,
                               struct drm_display_mode *adjusted_mode,
                               int x, int y,
                               struct drm_framebuffer *old_fb)

{
	// struct drm_device *dev = crtc->dev;
	struct pidock_framebuffer *pfb = to_pidock_fb(crtc->primary->fb);
	// struct pidock_device *pidock = dev->dev_private;
	int color_depth = 0;

	DRM_INFO("pidock_crtc_mode_set:");

	pidock_vidreg_lock();

	// TODO: Send mode information to userland
	pidock_set_color_depth(color_depth);

	// pidock_set_vid_cmds(adjusted_mode);
	pidock_set_blank(DRM_MODE_DPMS_ON);
	pidock_vidreg_unlock();

	if (old_fb) {
		struct pidock_framebuffer *pold_fb = to_pidock_fb(old_fb);
		pold_fb->active = false;
	}
	pfb->active = true;

	/* damage all of it */
	pidock_nl_handle_damage(pfb, 0, 0, pfb->base.width, pfb->base.height);
	return 0;
}


static void pidock_crtc_disable(struct drm_crtc *crtc)
{
	DRM_INFO("pidock_crtc_disable:");
	pidock_crtc_dpms(crtc, DRM_MODE_DPMS_OFF);
}

static int pidock_crtc_page_flip(struct drm_crtc *crtc,
	struct drm_framebuffer *fb,
	struct drm_pending_vblank_event *event,
	uint32_t page_flip_flags)
{
	/* stub */
	DRM_INFO("pidock_crtc_page_flip:");
	return 0;
}

static void pidock_crtc_prepare(struct drm_crtc *crtc)
{
	DRM_INFO("pidock_crtc_prepare:");
}

static void pidock_crtc_commit(struct drm_crtc *crtc)
{
	DRM_INFO("pidock_crtc_commit:");
	pidock_crtc_dpms(crtc, DRM_MODE_DPMS_ON);
}


static struct drm_crtc_helper_funcs pidock_helper_funcs = {
	.dpms = pidock_crtc_dpms,
	.mode_fixup = pidock_crtc_mode_fixup,
	.mode_set = pidock_crtc_mode_set,
	.prepare = pidock_crtc_prepare,
	.commit = pidock_crtc_commit,
	.disable = pidock_crtc_disable,
};

static void pidock_crtc_destroy(struct drm_crtc *crtc)
{
	drm_crtc_cleanup(crtc);
	kfree(crtc);
}

static const struct drm_crtc_funcs pidock_crtc_funcs = {
	.set_config = drm_crtc_helper_set_config,
	.destroy = pidock_crtc_destroy,
	.page_flip = pidock_crtc_page_flip,
};

static int pidock_crtc_init(struct drm_device *dev)
{
	struct drm_crtc *crtc;
	DRM_INFO("pidock_crtc_init:");

	crtc = kzalloc(sizeof(struct drm_crtc) + sizeof(struct drm_connector *), GFP_KERNEL);
	if (crtc == NULL)
		return -ENOMEM;

	drm_crtc_init(dev, crtc, &pidock_crtc_funcs);
	drm_crtc_helper_add(crtc, &pidock_helper_funcs);

	return 0;
}

static const struct drm_mode_config_funcs pidock_mode_funcs = {
	.fb_create = pidock_fb_user_fb_create,
	.output_poll_changed = NULL,
};


int pidock_modeset_init(struct drm_device *dev)
{
	struct drm_encoder *encoder;
	DRM_INFO("pidock_modeset_init:");
	drm_mode_config_init(dev);

	dev->mode_config.min_width = 640;
	dev->mode_config.min_height = 480;
	
	dev->mode_config.max_width = 3840;
	dev->mode_config.max_height = 2160;

	dev->mode_config.prefer_shadow = 0;
	dev->mode_config.preferred_depth = 24;

	dev->mode_config.funcs = &pidock_mode_funcs;

	drm_mode_create_dirty_info_property(dev);

	pidock_crtc_init(dev);

	encoder = pidock_encoder_init(dev);

	pidock_connector_init(dev, encoder);

	return 0;
}

void pidock_modeset_cleanup(struct drm_device *dev)
{
	drm_mode_config_cleanup(dev);
}
