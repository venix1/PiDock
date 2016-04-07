#include <drm/drmP.h>
#include "pidock_drv.h"

int pidock_output_init(struct drm_device *dev) {
	struct pidock_device *pidock = dev->dev_private;
	struct pidock_output *output;
	int idx;

	for(idx=0;idx<PIDOCK_MAX_OUTPUT; ++idx)
	{
		if (pidock->output[idx] == NULL)
			break;
	}

	if (idx == PIDOCK_MAX_OUTPUT)
		return -1;

	output = kmalloc(sizeof(struct pidock_output), GFP_KERNEL);
	output->idx = idx;
	output->crtc = pidock_crtc_init(dev);
	if (IS_ERR_OR_NULL(output->crtc))
		goto fail;
	if (idx == 0) {
		output->encoder = pidock_encoder_init(dev);
		if (IS_ERR_OR_NULL(output->encoder))
			goto fail_encoder;
	} 
	else {
		output->encoder = pidock->output[0]->encoder;
	}
	DRM_INFO("pidock_output_init: %d %p", idx, output->encoder);
	output->connector = pidock_connector_init(dev, output->encoder);
	if (IS_ERR_OR_NULL(output->connector))
		goto fail_connector;
	// pidock_fbdev_init(dev);

	pidock->output[idx] = output; 
	return idx;

fail_connector:
    //pidock_encoder_cleanup(output->encoder);
fail_encoder:
    // pidock_crtc_cleanup(output->crtc);
fail:
kfree(output);
    return -1;
}

int pidock_output_cleanup(struct drm_device *dev, struct pidock_output *output) {
	// struct pidock_device *pidock = dev->dev_private;

    if (output == NULL)
        return 0;

    // pidock_connector_cleanup(output->connector);
    // pidock_encoder_cleanup(output->encoder);
    // pidock_crtc_cleanup(output->crtc);

    kfree(output);

    return 0;
}
