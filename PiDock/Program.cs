using System;
using LibDRM;

namespace PiDock.Source
{
	public struct Display {
		public int width;
		public int height;
		public byte[] framebuffer;

		public Display(int width_, int height_) {
			width = width_;
			height = height_;
			framebuffer = null;
		}
	}
	class MainClass
	{

		public static void Main (string[] args)
		{
			DRMCard mCard;
			Encoder mEncoder;
			Display mDisplay;
			PiDockSocket mPiDock;

			// ZRE Beacon
			/*
			ZRE.__init__(self, loop)
			*/

			// Acquire Framebuffer
			// TODO: Acquire exact card dynamically
			mCard = new DRMCard("/dev/dri/card1");

			/*
			if (mCard.Framebuffers.Length < 1) 
				return 1;
			*/

			// TODO: Acquire FB dynamically
			DRMFramebuffer fb = mCard.GetFramebuffer(27);
			// size = r['height'] * r['pitch']
			// r = self.drm.map_dumb(1)
			// self.fb = self.drm.mmap64(size, r['offset'])

			// TODO: Get resolution from DRM
			// For now deafult to 1920x1080 and resize later

			mDisplay = new Display (1920, 1080);

			// Listen for netlink events
			mPiDock = new PiDockSocket();

			// Encoder
			mEncoder = new Encoder(mDisplay);

			//	self.clock = time.time()
			//  EventManager.register('fb/damage', self.on_damage)
		}

		public void MainLoop() {
/*
			"""main processing function."""
			if self.server.is_active:
				self.pidock.run_once()

				EventManager.update()

				# Fix to 60 FPS
			if time.time() - self.clock < .015:
				return True
					# 1 FPS
					if time.time() - self.clock < 1:
						return True

							# self.server.fillRect((0,0), (200,200), 0xFFFFFFFF)
							# self.server.markRectAsModified((0, 0), (self.width, self.height))
							self.server.process_events(0)
							# time.sleep(1)

							return True
								*/
			
		}
		public void OnDamage(object sender, EventArgs e) {
			// self.server.mark_rect_as_modified(0, 0, self.width, self.height) 
		}

		public void OnHello(object sender, EventArgs e) {
			/*
			 * """handler for ZRE hello message."""
			self.hello(peer)
			msg = {
				'op': 'connect',
				'width': 1680,
				'height': 1050
			}
				self.whisper(peer, msgpack.packb(msg))
			*/

		}
		public void OnWhisper(object sender, EventArgs e) {
			/*

				"""handler for ZRE whisper message."""
				print(type(msg), msg)
				content = msgpack.unpackb(msg.content, encoding='utf-8')
				print(content)

				op = content.get('op', None)
				if op == 'ready':
					time.sleep(1)
					# TODO: Solve race issue if client is slow setting up port.
					# Really client should set this up before sending packet
					self.server.reverseConnection(content['ip'], content['port'])
					elif op == 'display':
					edid = b64decode(content['edid'])
					self.pidock.load_edid(edid)

					msg = {
					'op': 'connect',
					}
					self.whisper(peer, msgpack.packb(msg))
					else:
					raise Exception('Unkown op:' + str(op))

*/
		}
	}
}
