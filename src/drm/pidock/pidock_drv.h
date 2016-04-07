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

#ifndef PIDOCK_DRV_H
#define PIDOCK_DRV_H

#include <drm/drm_gem.h>

#define PIDOCK_NAME 		"pidock"
#define PIDOCK_DESC			"PiDock"
#define PIDOCK_DATE			"20150420"

#define PIDOCK_MAJOR		0
#define PIDOCK_MINOR		0
#define PIDOCK_PATCHLEVEL	1

#define PIDOCK_MAX_OUTPUT   255

#define to_pidock_bo(x) container_of(x, struct pidock_gem_object, base)
#define to_pidock_fb(x) container_of(x, struct pidock_framebuffer, base)

extern struct device pidock_bus;

extern struct pidock_device *pidock_dev;

// static struct pidock_device pidock_dev;

struct pidock_gem_object {
	struct drm_gem_object base;
	struct page **pages;
	void *vmapping;
    bool use_dma_buf;

	/* Needed ? */
	struct sg_table *sg;
	unsigned int flags;
};

struct pidock_framebuffer {
	struct drm_framebuffer base;
	struct pidock_gem_object *obj;

	bool active; 
	int x1, y1, x2, y2; /* dirty rect */
	spinlock_t dirty_lock;
};

struct pidock_output {
	unsigned char         idx;
	struct drm_connector *connector;
	struct drm_crtc      *crtc;
	struct drm_encoder   *encoder;
	struct pidock_fbdev  *fbdev;
};

struct pidock_device {
	struct device *dev;
	struct drm_device *ddev;
	struct sock *nl_sk;

	struct pidock_fbdev *fbdev;
	char mode_buf[1024];
	uint32_t mode_buf_len;

	uint32_t gnl_seq;

	struct pidock_output* output[PIDOCK_MAX_OUTPUT];
};

int pidock_driver_unload(struct drm_device *dev);
int pidock_driver_load(struct drm_device *dev, unsigned long flags);

int pidock_output_init(struct drm_device *dev);
int pidock_output_cleanup(struct drm_device *dev, struct pidock_output *output);

struct drm_crtc* pidock_crtc_init(struct drm_device *dev);
int pidock_crtc_cleanup(struct drm_crtc* crtc);

struct drm_connector* pidock_connector_init(struct drm_device *dev, struct drm_encoder *encoder);
int pidock_connector_cleanup(struct drm_connector *connector);

struct drm_encoder *pidock_encoder_init(struct drm_device *dev);
int pidock_encoder_cleanup(struct drm_encoder *encoder);

int pidock_fbdev_init(struct drm_device *dev);
void pidock_fbdev_cleanup(struct drm_device *dev);
struct drm_framebuffer *
pidock_fb_user_fb_create(struct drm_device *dev,
	struct drm_file *file,
	struct drm_mode_fb_cmd2 *mode_cmd);

int pidock_drm_gem_mmap(struct file *filp, struct vm_area_struct *vma);

int pidock_dumb_create(struct drm_file *file,
                    struct drm_device *dev,
                    struct drm_mode_create_dumb *args);

int pidock_gem_fault(struct vm_area_struct *vma, struct vm_fault *vmf);
void pidock_gem_free_object(struct drm_gem_object *gem_obj);
int pidock_gem_get_pages(struct pidock_gem_object *obj);
int pidock_gem_mmap(struct drm_file *file, struct drm_device *dev,
                 uint32_t handle, uint64_t *offset);
struct pidock_gem_object *pidock_gem_alloc_object(struct drm_device *dev,
	size_t size);
void pidock_gem_put_pages(struct pidock_gem_object *obj);
int pidock_gem_vmap(struct pidock_gem_object *obj);

struct drm_gem_object * gem_prime_import_sg_table(
	struct drm_device *dev,
	struct dma_buf_attachment *attach,
	struct sg_table *sgt);
struct drm_gem_object *pidock_gem_prime_import(struct drm_device *dev,
				struct dma_buf *dma_buf);




int pidock_modeset_init(struct drm_device *dev);
void pidock_modeset_cleanup(struct drm_device *dev);

int pidock_nl_init(struct pidock_device *pidock);
void pidock_nl_cleanup(struct pidock_device *pidock);
int pidock_nl_handle_damage(
	struct pidock_framebuffer *pfb,
	int x, int y,
	int w, int h);

int pidock_bus_init(void);
void pidock_bus_cleanup(void);

#endif
