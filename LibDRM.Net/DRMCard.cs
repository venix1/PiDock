using System;

namespace LibDRM
{
	struct drm_mode_card_res {
		ulong fb_id_ptr;
		ulong crtc_id_ptr;
		ulong connector_id_ptr;
		ulong encoder_id_ptr;
		uint count_fbs;
		uint count_crtcs;
		uint count_connectors;
		uint count_encoders;
		uint min_width;
		uint max_width;
		uint min_height;
		uint max_height;
	}

	public class DRMFramebuffer {
	}

	public class DRMCard
	{
		const uint DRM_IOCTL_MODE_GETRESOURCES = 0;

		public class Resources {
		}


		public DRMCard (string device)
		{
		}

		private unsafe void GetResources() {
			// int status = ioctl (fd, DRM_IOCTL_MODE_GETRESOURCES, &mDRMResources);
		}

		public DRMFramebuffer GetFramebuffer(int id) {
			return null;
		}

		private void Cleanup() {
		}

		private void refresh() {
			Cleanup();
			// TODO: Evaulate how this is done.

			// mDRMResources = ioctl(mFD, 

			/*
			status = clibdrm.ioctl(self.fd,
				clibdrm.DRM_IOCTL_MODE_GETRESOURCES,
				&self.drm_resources)

				assert status == 0, status

			if self.drm_resources.count_connectors:
				size = self.drm_resources.count_connectors * sizeof(__u64)
					self.drm_resources.connector_id_ptr = <__u64> PyMem_Malloc(size)
					memset(<void*>self.drm_resources.connector_id_ptr, 0, size)

					if self.drm_resources.count_crtcs:
						size = self.drm_resources.count_crtcs * sizeof(__u64)
						self.drm_resources.crtc_id_ptr = <__u64> PyMem_Malloc(size)
						memset(<void*>self.drm_resources.crtc_id_ptr, 0, size)

					if self.drm_resources.count_encoders:
						size = self.drm_resources.count_encoders * sizeof(__u64)
						self.drm_resources.encoder_id_ptr = <__u64> PyMem_Malloc(size)
						memset(<void*>self.drm_resources.encoder_id_ptr, 0, size)

					if self.drm_resources.count_fbs:
						size = self.drm_resources.count_fbs * sizeof(__u64)
						self.drm_resources.fb_id_ptr = <__u64> PyMem_Malloc(size)
						memset(<void*>self.drm_resources.fb_id_ptr, 0, size)

						status = clibdrm.ioctl(self.fd,
							clibdrm.DRM_IOCTL_MODE_GETRESOURCES,
							&self.drm_resources)
						assert status == 0, status

					cdef __u64* crtc_ids = <__u64*>self.drm_resources.crtc_id_ptr
					for i in range(self.drm_resources.count_crtcs):
						self.get_crtc(crtc_ids[i])
						# self.crtcs.append(DRMCRTC(self, crtc_ids[i]))
						# print(i, crtc_ids[i])
						*/
		}


		

		/*
		cdef int DRM_IOCTL_SET_MASTER
		cdef int DRM_IOCTL_MODE_GETRESOURCES
		cdef int DRM_IOCTL_MODE_GETCRTC
		cdef int DRM_IOCTL_MODE_MAP_DUMB
		cdef int DRM_IOCTL_MODE_GETFB
		*/

		/*
		[DllImport("libc.so")]
		static unsafe extern int ioctl(int, ulong, ....);

		[DllImport("libc.so")]
		static unsafe extern void* mmap64(void*, ulong, uint, int, int, ulong);
		enum int MAP_FAILED;
		enum int MAP_SHARED;
		enum int PROT_READ;
		enum int PROT_WRITE;
		*/

	}
}