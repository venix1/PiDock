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

#define PIDOCK_MSG_SIZE (PAGE_SIZE-GENL_HDRLEN)

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
	PIDOCK_A_TILE_RECT,
	PIDOCK_A_TILE_DATA,
	PIDOCK_A_OUTPUT_ID,
    PIDOCK_A_FB_ID,
	__PIDOCK_A_MAX,
};

#define PIDOCK_A_MAX (__PIDOCK_A_MAX - 1)

static struct nla_policy pidock_genl_policy[PIDOCK_A_MAX + 1] = {
	[PIDOCK_A_OUTPUT_ID] = { .type = NLA_U32 },
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
/* obsolete by mmap buffer. */
static int pidock_fb_refresh(struct sk_buff *skb, struct genl_info *info)
{
	/*
    struct nlattr *tb[PIDOCK_A_MAX+1];
    struct nlmsghdr *nlh = nlmsg_hdr(skb);
	int err;
	*/

	DRM_INFO("pidock_nl_fb_refresh: ");
	// err = nlmsg_parse(nlh, 0, tb, PIDOCK_A_MAX, pidock_genl_policy);

	return 0;
}

/* Dynamically add connector. */
// pidock_gnl_doit_addconn
static int pidock_doit_getfb(struct sk_buff *skb, struct genl_info *info)
{
	struct sk_buff *msg;
	void *reply;
	// struct nlattr  *nla;
	int id;

	if (info->attrs[PIDOCK_A_OUTPUT_ID] == NULL) {
		DRM_INFO("pidock_nl_connector_add: no ID");
		// err invalid msg
		return -1;
	}

	id = nla_get_u32(info->attrs[PIDOCK_A_OUTPUT_ID]);
	DRM_INFO("pidock_gnl_doit_getfb: %d", id);

    if (pidock_dev->output[id] == NULL)
        return 0;

	msg = nlmsg_new(NLMSG_DEFAULT_SIZE, GFP_KERNEL);
	if (!msg)
		return -ENOMEM;

	reply = genlmsg_put_reply(msg, info, &pidock_gnl_family, 0, info->genlhdr->cmd);
	nla_put_u32(msg, PIDOCK_A_OUTPUT_ID, id);

    if (pidock_dev->output[id]->crtc->primary->fb) {
	    nla_put_u32(msg, PIDOCK_A_FB_ID,
                    pidock_dev->output[id]->crtc->primary->fb->base.id);
/*
if (fb->funcs->create_handle) {
if (file_priv->is_master || capable(CAP_SYS_ADMIN) ||
drm_is_control_client(file_priv)) {
ret = fb->funcs->create_handle(fb, file_priv,
&r->handle);
}
}
	    nla_put_u32(skb, PIDOCK_A_FB_HANDLE, pfb->base.base.id);
*/
    }
    else {
        DRM_INFO("no primary fb");
	    nla_put_u32(msg, PIDOCK_A_FB_ID, 0);
    }

	genlmsg_end(msg, reply);
	return genlmsg_reply(msg, info);
}
static int pidock_connector_add(struct sk_buff *skb, struct genl_info *info)
{
	struct sk_buff *msg;
	void *reply;
	// struct nlattr  *nla;
	int id;

	if (info->attrs[PIDOCK_A_OUTPUT_ID] == NULL) {
		DRM_INFO("P: %p", info->attrs[0]);
		DRM_INFO("P: %p", info->attrs[1]);
		DRM_INFO("P: %p", info->attrs[2]);
		DRM_INFO("P: %p", info->attrs[PIDOCK_A_OUTPUT_ID]);
		DRM_INFO("P: %d", PIDOCK_A_OUTPUT_ID);
		DRM_INFO("pidock_nl_connector_add: no ID");
		// err invalid msg
		return -1;
	}

	id = nla_get_u32(info->attrs[PIDOCK_A_OUTPUT_ID]);
	DRM_INFO("pidock_nl_connector_add: %d", id);

	id = pidock_output_init(pidock_dev->ddev);
	if (id < 0)
		return id;

	msg = nlmsg_new(NLMSG_DEFAULT_SIZE, GFP_KERNEL);
	if (!msg)
		return -ENOMEM;

	reply = genlmsg_put_reply(msg, info, &pidock_gnl_family, 0, info->genlhdr->cmd);
	nla_put_u32(msg, PIDOCK_A_OUTPUT_ID, id);


	nla_put_u32(msg, PIDOCK_A_FB_ID,
                pidock_dev->output[id]->crtc->primary->fb->base.id);

	genlmsg_end(msg, reply);
	return genlmsg_reply(msg, info);
}

/* Dynamically remove connector. */
static int pidock_connector_remove(struct sk_buff *skb, struct genl_info *info)
{
	DRM_INFO("pidock_nl_connector_remove: ");
    /* Userspace should send 32-bit identifier. */
	return 0;
}

enum {
	PIDOCK_C_FB_DIRTY,
	PIDOCK_C_FB_REFRESH,
	PIDOCK_C_CONNECTOR_ADD,
	PIDOCK_C_CONNECTOR_REMOVE,
    PIDOCK_C_GET_FB,
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
	{
		.cmd = PIDOCK_C_CONNECTOR_ADD,
		.flags = 0,
		.policy = pidock_genl_policy,
		.doit = pidock_connector_add,
		.dumpit = NULL,
    },
	{
		.cmd = PIDOCK_C_CONNECTOR_REMOVE,
		.flags = 0,
		.policy = pidock_genl_policy,
		.doit = pidock_connector_remove,
		.dumpit = NULL,
    },
    {
        .cmd = PIDOCK_C_GET_FB,
        .flags = 0,
        .policy = pidock_genl_policy,
        .doit = pidock_doit_getfb,
        .dumpit = NULL,
    }

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
	// struct nlattr  *nla;
	void *msg_head;
	int rc;

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

    rect_set(&rect, x, y, width, height);

	skb = genlmsg_new(PIDOCK_MSG_SIZE, GFP_KERNEL);
	if (skb == NULL)
        goto error;

    msg_head = genlmsg_put(skb, 0, 0, &pidock_gnl_family, 0, PIDOCK_C_FB_DIRTY);
	if (msg_head == NULL) {
	    rc = -ENOMEM;
       	goto free;
	}

    nla_put(skb, PIDOCK_A_TILE_RECT, sizeof(struct rect), &rect);
    nla_put_u32(skb, PIDOCK_A_FB_ID, pfb->base.base.id);
	genlmsg_end(skb, msg_head);

	rc = genlmsg_multicast(&pidock_gnl_family, skb, 0, 0, 0);
	if (rc && rc != -ESRCH)
	    goto free;

	return 0;
free:
	nlmsg_free(skb);
error:
	DRM_INFO("Failed to send Damage Update: %d", rc);
	return rc;
}
