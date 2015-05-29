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
//#include <drm/drm_crtc.h>
//#include <drm/drm_edid.h>
#include <drm/drm_crtc_helper.h>


#include "pidock_drv.h"

static void pidock_enc_destroy(struct drm_encoder *encoder)
{
	DRM_INFO("pidock_enc_destroy:");
	drm_encoder_cleanup(encoder);
	kfree(encoder);
}

static void pidock_encoder_disable(struct drm_encoder *encoder)
{
	DRM_INFO("pidock_encoder_disable:");
}

static bool pidock_mode_fixup(struct drm_encoder *encoder,
                           const struct drm_display_mode *mode,
                           struct drm_display_mode *adjusted_mode)
{
	return true;
}

static void pidock_encoder_prepare(struct drm_encoder *encoder)
{
	DRM_INFO("pidock_encoder_prepare:");
}

static void pidock_encoder_commit(struct drm_encoder *encoder)
{
	DRM_INFO("pidock_encoder_commit:");
}

static void pidock_encoder_mode_set(struct drm_encoder *encoder,
                                 struct drm_display_mode *mode,
                                 struct drm_display_mode *adjusted_mode)
{
	DRM_INFO("pidock_encoder_mode_set:");
}

static void
pidock_encoder_dpms(struct drm_encoder *encoder, int mode)
{
	DRM_INFO("pidock_encoder_dpms:");
}

static const struct drm_encoder_helper_funcs pidock_helper_funcs = {
	.dpms = pidock_encoder_dpms,
	.mode_fixup = pidock_mode_fixup,
	.prepare = pidock_encoder_prepare,
	.mode_set = pidock_encoder_mode_set,
	.commit = pidock_encoder_commit,
	.disable = pidock_encoder_disable,
};

static const struct drm_encoder_funcs pidock_enc_funcs = {
	.destroy = pidock_enc_destroy,
};

struct drm_encoder *pidock_encoder_init(struct drm_device *dev)
{
	struct drm_encoder *encoder;
	DRM_INFO("pidock_encoder_init:");

	encoder = kzalloc(sizeof(struct drm_encoder), GFP_KERNEL);
	if (!encoder)
		return NULL;

	drm_encoder_init(dev, encoder, &pidock_enc_funcs, DRM_MODE_ENCODER_TMDS);
	drm_encoder_helper_add(encoder, &pidock_helper_funcs);
	encoder->possible_crtcs = 1;
	return encoder;
}
