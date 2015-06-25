/*
 * Copyright (C) 2015 Daniel Green <venix1@gmail.com>
 * 
 * This file is subject to the terms and conditions of the GNU General Public
 * License v2. See the file COPYING in the main directory of this archive for
 * more details.
 */

#include <drm/drmP.h>
#include <drm/drm_fb_helper.h>
#include <net/netlink.h>
#include <net/genetlink.h>

#include "pidock_drv.h"

#define PIDOCK_MSG_SIZE ((PAGE_SIZE*15)-GENL_HDRLEN)

struct rect{
	unsigned int x;
	unsigned int y;
	unsigned int width;
	unsigned int height;
	unsigned int pitch;
};

void rect_set(struct rect* rect, int x, int y, int width, int height)
{
	rect->x = x;
	rect->y = y;
	rect->width = width;
	rect->height = height;
}

enum {
	PIDOCK_A_UNSPEC,
	PIDOCK_A_TILE_PITCH,
	PIDOCK_A_TILE_RECT,
	PIDOCK_A_TILE_DATA,
	__PIDOCK_A_MAX,
};

#define PIDOCK_A_MAX (__PIDOCK_A_MAX - 1)

static struct nla_policy pidock_genl_policy[PIDOCK_A_MAX + 1] = {
	[PIDOCK_A_TILE_RECT] = { .len = sizeof(struct rect) },
	[PIDOCK_A_TILE_DATA] = { .type = NLA_BINARY, .len = PIDOCK_MSG_SIZE },
};

static struct genl_family pidock_gnl_family = {
	.id = GENL_ID_GENERATE,
	.hdrsize = 0,
	.name = "pidock",
	.version = 1,
	.maxattr = PIDOCK_A_MAX,
};

/* Send entire framebuffer */
static int pidock_fb_refresh(struct sk_buff *skb, struct genl_info *info)
{
	return 0;
}

enum {
	PIDOCK_C_FB_DIRTY,
	PIDOCK_C_FB_REFRESH,
	__PIDOCK_C_MAX,
};

static struct genl_ops pidock_gnl_ops[] = {
	{
		.cmd = PIDOCK_C_FB_REFRESH,
		.flags = 0,
		.policy = pidock_genl_policy,
		.doit = pidock_fb_refresh,
		.dumpit = NULL,
	},
};

static const struct genl_multicast_group pidock_multicast_groups[] = {
	{ .name = "pidock_mc_group", },
};

int pidock_nl_init(struct pidock_device *pidock)
{
	int rc;

	rc = genl_register_family_with_ops_groups(&pidock_gnl_family,
		pidock_gnl_ops, pidock_multicast_groups);
	if (rc)
		goto error;

	DRM_INFO("Registered PiDock family");
error:
	return rc;
}

void pidock_nl_cleanup(struct pidock_device *pidock)
{
	genl_unregister_family(&pidock_gnl_family);
}

/*
 * Transmits damage updates as netlink messages over multicast.
 */
int pidock_nl_handle_damage(
	struct pidock_framebuffer *pfb,
	int x,     int y,
	int width, int height)
{
	// struct drm_device *dev = pfb->base.dev;
	// struct pidock_device *pidock = dev->dev_private;
	struct rect rect;
	struct sk_buff *skb;
	struct nlattr  *nla;
	void *msg_head;
	int rc;

	int pitch = width * DIV_ROUND_UP(pfb->base.depth, 8);
	int bytes = pitch * height;

	/* Map framebuffer for access */
	if (!pfb->obj->vmapping) {
		rc = pidock_gem_vmap(pfb->obj);
		if (rc == -ENOMEM) {
			DRM_ERROR("failed to vmap fb\n");
			return 0;
		}
		if (!pfb->obj->vmapping) {
			DRM_ERROR("failed to vmapping\n");
			return 0;
		}
	}
	DRM_INFO("pidock_nl_handle_damage: pfb:%p vmap:%p", pfb, pfb->obj->vmapping);


	while(bytes > 0)
	{
		// Calculate packet size
		int hline;
		int len = bytes > PIDOCK_MSG_SIZE ? PIDOCK_MSG_SIZE : bytes;
		int rows = len / pitch;
		len = rows * pitch; // Don't want to truncate mid line
		bytes -= len;

		// Determine number of rows we can send.
		rows = rows < height ? rows : height;
		rect_set(&rect, x, y, width, rows);
		rect.pitch = pitch;

		// DRM_INFO("Msg - Remaining: %d Bytes: %d Rows: %d Pitch: %d", bytes, len, rows, pitch);

		skb = genlmsg_new(len + 32, GFP_KERNEL);
		// skb = genlmsg_new(PIDOCK_MSG_SIZE, GFP_KERNEL);
		// skb = genlmsg_new(GENLMSG_DEFAULT_SIZE, GFP_ATOMIC);
		if (skb == NULL)
			goto error;

		msg_head = genlmsg_put(skb, 0, 0, &pidock_gnl_family, 0, PIDOCK_C_FB_DIRTY);
		if (!msg_head) {
			rc = -ENOMEM;
			goto free;
		}

		rc = nla_put(skb, PIDOCK_A_TILE_RECT, sizeof(struct rect), &rect);
		if (rc)
			goto free;

		nla = nla_reserve(skb, PIDOCK_A_TILE_DATA, len);
		if (!nla) {
			DRM_INFO("Tile data too large for buffer");
			goto free;
		}
		/* Copy pixels from Framebuffer to message */
		for(hline=0; hline < rows; ++hline) {
			// void *tmp = kmalloc(pitch, GFP_KERNEL);
			void *base = pfb->obj->vmapping + pfb->base.pitches[0] * (y+hline) + x;
			memcpy(nla_data(nla) + (hline*pitch), base, pitch);
		}

		genlmsg_end(skb, msg_head);

		rc = genlmsg_multicast(&pidock_gnl_family, skb, 0, 0, 0);
		if (rc && rc != -ESRCH)
			goto free;

		height -= rows;
		y += rows;
	}

	return 0;
free:
	nlmsg_free(skb);
error:
	DRM_INFO("Failed to send Damage Update: %d", rc);
	return rc;
}
