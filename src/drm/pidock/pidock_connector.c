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
#include <drm/drm_edid.h>
#include <drm/drm_crtc_helper.h>

#include "pidock_drv.h"

/* Query PiDock Daemon for EDID information */
static u8 *pidock_get_edid(struct pidock_device *pidock)
{
	/* This should come from userland tool. For prototyping
	 * we're using a generic 1920x1080 edid.
	 */
	static const u8 generic_edid[128] = {

	/* 1680x150 EDID
	0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x4c, 0xa3, 0x47, 0x4a, 0x00, 0x00, 0x00, 0x00, 
	0x00, 0x12, 0x01, 0x03, 0x80, 0x25, 0x17, 0x78, 0x0a, 0x87, 0xf5, 0x94, 0x57, 0x4f, 0x8c, 0x27,
	0x27, 0x50, 0x54, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
	0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x70, 0x2f, 0x90, 0xa0, 0x60, 0x1a, 0x32, 0x40, 0x30, 0x20,
	0x26, 0x00, 0x6d, 0xe4, 0x10, 0x00, 0x00, 0x19, 0x00, 0x00, 0x00, 0x0f, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x41, 0x5f, 0x05, 0x19, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x00, 0x53,
	0x41, 0x4d, 0x53, 0x55, 0x4e, 0x47, 0x0a, 0x20, 0x20, 0x20, 0x20, 0x20, 0x00, 0x00, 0x00, 0xfe,
	0x00, 0x31, 0x37, 0x30, 0x4d, 0x54, 0x30, 0x32, 0x2d, 0x47, 0x30, 0x31, 0x0a, 0x20, 0x00, 0x18
 */

		0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00,
		0x31, 0xd8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x05, 0x16, 0x01, 0x03, 0x6d, 0x32, 0x1c, 0x78,
		0xea, 0x5e, 0xc0, 0xa4, 0x59, 0x4a, 0x98, 0x25,
		0x20, 0x50, 0x54, 0x00, 0x00, 0x00, 0xd1, 0xc0,
		0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
		0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02, 0x3a,
		0x80, 0x18, 0x71, 0x38, 0x2d, 0x40, 0x58, 0x2c,
		0x45, 0x00, 0xf4, 0x19, 0x11, 0x00, 0x00, 0x1e,
		0x00, 0x00, 0x00, 0xff, 0x00, 0x4c, 0x69, 0x6e,
		0x75, 0x78, 0x20, 0x23, 0x30, 0x0a, 0x20, 0x20,
		0x20, 0x20, 0x00, 0x00, 0x00, 0xfd, 0x00, 0x3b,
		0x3d, 0x42, 0x44, 0x0f, 0x00, 0x0a, 0x20, 0x20,
		0x20, 0x20, 0x20, 0x20, 0x00, 0x00, 0x00, 0xfc,
		0x00, 0x4c, 0x69, 0x6e, 0x75, 0x78, 0x20, 0x46,
		0x48, 0x44, 0x0a, 0x20, 0x20, 0x20, 0x00, 0x05,
	};

	u8 *edid;
	DRM_INFO("pidock_get_edid:");

	edid = kzalloc(sizeof(struct edid), GFP_KERNEL);
	memcpy(edid, generic_edid, 128);

	return edid;
}

static int pidock_get_modes(struct drm_connector *connector)
{
	struct pidock_device *pidock = connector->dev->dev_private;
	struct edid *edid;
	int retval;

	DRM_INFO("pidock_get_modes:");
	/* TODO: Support an array of EDID */
	
	edid = (struct edid *)pidock_get_edid(pidock);
	if (!edid) {
		drm_mode_connector_update_edid_property(connector, NULL);
		return 0;
	}

	drm_mode_connector_update_edid_property(connector, edid);
	retval = drm_add_edid_modes(connector, edid);
	kfree(edid);

	return retval;
}

static int pidock_mode_valid(
	struct drm_connector *connector,
	struct drm_display_mode *mode)
{
	// struct pidock_device *pidock = connector->dev->dev_private;

	DRM_INFO("pidock_mode_valid:");
	/* stub */

	return MODE_OK;
}

static enum drm_connector_status
pidock_detect(struct drm_connector *connector, bool force)
{
	DRM_INFO("pidock_detect:");
	if (drm_device_is_unplugged(connector->dev))
		return connector_status_disconnected;

	/* TODO: Maintain and report state via netlink */
	DRM_INFO("pidock_detect: exit");
	return connector_status_connected;
}

static struct drm_encoder*
pidock_best_single_encoder(struct drm_connector *connector)
{
	int enc_id = connector->encoder_ids[0];
	DRM_INFO("pidock_best_single_encoder: %d", enc_id);
	return drm_encoder_find(connector->dev, enc_id);
}

static int pidock_connector_set_property(struct drm_connector *connector,
                                      struct drm_property *property,
                                      uint64_t val)
{
	DRM_INFO("pidock_connector_set_property:");
	return 0;
}

static void pidock_connector_destroy(struct drm_connector *connector)
{
	DRM_INFO("pidock_connector_destroy:");
	drm_connector_unregister(connector);
	drm_connector_cleanup(connector);
	kfree(connector);
}

static struct drm_connector_helper_funcs pidock_connector_helper_funcs = {
	.get_modes = pidock_get_modes,
	.mode_valid = pidock_mode_valid,
	.best_encoder = pidock_best_single_encoder,
};

static struct drm_connector_funcs pidock_connector_funcs = {
	.dpms = drm_helper_connector_dpms,
	.detect = pidock_detect,
	.fill_modes = drm_helper_probe_single_connector_modes,
	.destroy = pidock_connector_destroy,
	.set_property = pidock_connector_set_property,
};

struct drm_connector* pidock_connector_init(struct drm_device *dev, struct drm_encoder *encoder)
{
	struct drm_connector *connector;
	DRM_INFO("pidock_connector_init:");

	connector = kzalloc(sizeof(struct drm_connector), GFP_KERNEL);
	if (!connector)
		return ERR_PTR(-ENOMEM);

	drm_connector_init(dev, connector, &pidock_connector_funcs, DRM_MODE_CONNECTOR_DVII);
	drm_connector_helper_add(connector, &pidock_connector_helper_funcs);

	drm_connector_register(connector);
	drm_mode_connector_attach_encoder(connector, encoder);

	drm_object_attach_property(&connector->base,
		dev->mode_config.dirty_info_property,
		1);

	return connector;
}
