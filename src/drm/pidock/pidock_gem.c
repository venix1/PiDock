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
#include <linux/dma-buf.h>

struct pidock_gem_object *pidock_gem_alloc_object(struct drm_device *dev,
                                            size_t size)
{
	struct pidock_gem_object *obj;
	DRM_INFO("pidock_gem_alloc_object:");

	obj = kzalloc(sizeof(*obj), GFP_KERNEL);
	if (obj == NULL)
		return NULL;

	if (drm_gem_object_init(dev, &obj->base, size) != 0) {
		kfree(obj);
		return NULL;
	}

	DRM_INFO("    object: %p", obj);
	return obj;
}

static int
pidock_gem_create(struct drm_file *file,
               struct drm_device *dev,
               uint64_t size,
               uint32_t *handle_p)
{
	struct pidock_gem_object *obj;
	int ret;
	u32 handle;
	DRM_INFO("pidock_gem_create:");

	size = roundup(size, PAGE_SIZE);

	obj = pidock_gem_alloc_object(dev, size);
	if (obj == NULL)
		return -ENOMEM;

	ret = drm_gem_handle_create(file, &obj->base, &handle);
	if (ret) {
		drm_gem_object_release(&obj->base);
		kfree(obj);
		return ret;
	}

	drm_gem_object_unreference(&obj->base);
	*handle_p = handle;
	return 0;
}

static void update_vm_cache_attr(struct pidock_gem_object *obj,
	struct vm_area_struct *vma)
{
	DRM_INFO("update_vm_cache_attr:");
	DRM_DEBUG_KMS("flags = 0x%x\n", obj->flags);

	vma->vm_page_prot =
		pgprot_noncached(vm_get_page_prot(vma->vm_flags));
}

int pidock_dumb_create(struct drm_file *file,
                    struct drm_device *dev,
                    struct drm_mode_create_dumb *args)
{
	DRM_INFO("pidock_dumb_create: width: %d height: %d", args->width, args->height);
	args->pitch = args->width * DIV_ROUND_UP(args->bpp, 8);
	args->size = args->pitch * args->height;
	return pidock_gem_create(file, dev,
		args->size, &args->handle);
}

int pidock_drm_gem_mmap(struct file *filp, struct vm_area_struct *vma)
{
	int ret;
	DRM_INFO("pidock_drm_gem_mmap:");


	ret = drm_gem_mmap(filp, vma);
	if (ret) {
		DRM_INFO("    Fail drm_gem_mmap: %d", ret);
		return ret;
	}

	vma->vm_flags &= ~VM_PFNMAP;
	vma->vm_flags |= VM_MIXEDMAP;

	update_vm_cache_attr(to_pidock_bo(vma->vm_private_data), vma);

	return 0;
}

int pidock_gem_fault(struct vm_area_struct *vma, struct vm_fault *vmf)
{
	struct pidock_gem_object *obj = to_pidock_bo(vma->vm_private_data);
	struct page *page;
	unsigned int page_offset;
	int ret = 0;
	DRM_INFO("pidock_gem_fault:");

	page_offset = ((unsigned long)vmf->virtual_address - vma->vm_start) >>
		PAGE_SHIFT;

	if (!obj->pages)
		return VM_FAULT_SIGBUS;

	page = obj->pages[page_offset];
	ret = vm_insert_page(vma, (unsigned long)vmf->virtual_address, page);
	switch (ret) {
		case -EAGAIN:
		case 0:
		case -ERESTARTSYS:
			return VM_FAULT_NOPAGE;
		case -ENOMEM:
			return VM_FAULT_OOM;
		default:
			return VM_FAULT_SIGBUS;
	}
}

int pidock_gem_get_pages(struct pidock_gem_object *obj)
{
	struct page **pages;
	DRM_INFO("pidock_gem_get_pages:");
	
	if (obj->pages)
		return 0;

	pages = drm_gem_get_pages(&obj->base);
	if (IS_ERR(pages))
		return PTR_ERR(pages);

	obj->pages = pages;
	DRM_INFO("    %p %p", obj, obj->pages);

	return 0;
}

void pidock_gem_put_pages(struct pidock_gem_object *obj)
{
	DRM_INFO("pidock_gem_put_pages:");

	if (obj->base.import_attach) {
		drm_free_large(obj->pages);
	}
	else {
		drm_gem_put_pages(&obj->base, obj->pages, false, false);
	}
	obj->pages = NULL;
}

int pidock_gem_vmap(struct pidock_gem_object *obj)
{
	int page_count = obj->base.size / PAGE_SIZE;
	int ret;
	DRM_INFO("pidock_gem_vmap:");

	if (obj->base.import_attach) {
		obj->vmapping = dma_buf_vmap(obj->base.import_attach->dmabuf);
		if (!obj->vmapping)
			return -ENOMEM;
		return 0;
	}

	ret = pidock_gem_get_pages(obj);
	if (ret) {
		DRM_INFO("pidock_gem_vmap: get_pages failed %d", ret);
		return ret;
	}

	obj->vmapping = vmap(obj->pages, page_count, 0, PAGE_KERNEL);
	if (!obj->vmapping)
		return -ENOMEM;
	DRM_INFO("    vmap:%p pages:%p count:%d", obj->vmapping, obj->pages, page_count);
	// memset(obj->vmapping, 255, obj->base.size);
	return 0;
}

void pidock_gem_vunmap(struct pidock_gem_object *obj)
{
	DRM_INFO("pidock_gem_vunmap:");
	if (obj->base.dma_buf) {
		// drm_buf_vunmap(obj->base.dma_buf);
		return;
	}
	vunmap(obj->vmapping);

	pidock_gem_put_pages(obj);
}

void pidock_gem_free_object(struct drm_gem_object *gem_obj)
{
	struct pidock_gem_object *obj = to_pidock_bo(gem_obj);

	DRM_INFO("pidock_gem_free_object:");

	if (obj->vmapping)
		pidock_gem_vunmap(obj);

	if (obj->pages)
		pidock_gem_put_pages(obj);

	drm_gem_free_mmap_offset(gem_obj);
}


/* the dumb interface doesn't work with the GEM straight MMAP
   interface, it expects to do MMAP on the drm fd, like normal */
int pidock_gem_mmap(struct drm_file *file, struct drm_device *dev,
                 uint32_t handle, uint64_t *offset)
{
	struct pidock_gem_object *gobj;
	struct drm_gem_object *obj;
	int ret = 0;

	DRM_INFO("pidock_gem_mmap:");

	mutex_lock(&dev->struct_mutex);
	obj = drm_gem_object_lookup(dev, file, handle);
	if (obj == NULL) {
		ret = -ENOENT;
		goto unlock;
	}
	gobj = to_pidock_bo(obj);

	ret = pidock_gem_get_pages(gobj);
	if (ret)
		goto out;
	ret = drm_gem_create_mmap_offset(obj);
	if (ret)
		goto out;

	*offset = drm_vma_node_offset_addr(&gobj->base.vma_node);

out:
	drm_gem_object_unreference(&gobj->base);
unlock:
	mutex_unlock(&dev->struct_mutex);
	return ret;
}

/* Gotta be honest, no idea what this is doing */
struct drm_gem_object *pidock_gem_prime_import(struct drm_device *dev,
				struct dma_buf *dma_buf)
{
	struct dma_buf_attachment *attach;
	struct sg_table *sg;
	struct pidock_gem_object *pobj;
	int ret, npages;

	/* need to attach */
	get_device(dev->dev);
	attach = dma_buf_attach(dma_buf, dev->dev);
	if (IS_ERR(attach)) {
		put_device(dev->dev);
		return ERR_CAST(attach);
	}

	get_dma_buf(dma_buf);

	sg = dma_buf_map_attachment(attach, DMA_BIDIRECTIONAL);
	if (IS_ERR(sg)) {
		ret = PTR_ERR(sg);
		goto fail_detach;
	}

	/* BEGIN prime_create */
	npages = dma_buf->size/PAGE_SIZE;

	pobj = pidock_gem_alloc_object(dev, dma_buf->size);
	if (!pobj) {
		goto fail_unmap;
	}
	pobj->sg = sg;
	pobj->pages = drm_malloc_ab(npages, sizeof(struct page *));
	if (pobj->pages == NULL) {
		DRM_ERROR("pobj pages is nULL %d\n", npages);
		ret = -ENOMEM;
		goto fail_unmap;
	}
	drm_prime_sg_to_page_addr_arrays(sg, pobj->pages, NULL, npages);
	/* END prime_create */

	pobj->base.import_attach = attach;

	return &pobj->base;

fail_unmap:
	dma_buf_unmap_attachment(attach, sg, DMA_BIDIRECTIONAL);
fail_detach:
	dma_buf_detach(dma_buf, attach);
	dma_buf_put(dma_buf);
	put_device(dev->dev);
	return ERR_PTR(ret);
}


struct drm_gem_object * gem_prime_import_sg_table(
	struct drm_device *dev,
	struct dma_buf_attachment *attach,
	struct sg_table *sgt)
{
	return NULL;
}
