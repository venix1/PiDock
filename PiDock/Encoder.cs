using System;

namespace PiDock.Source
{
	public struct Region {
		int x1, y1;
		int x2, y2;

		public int width {
			get { return x2 - x1; }

		}
	}
	public class CRC32Block
	{
		private Display mDisplay;
		private uint[] mCrc;

		public CRC32Block(Display display) {
			mDisplay = display;
			mCrc = new uint[mDisplay.width * mDisplay.height];
		}
	}

	public class Encoder {
		private CRC32Block mCrcBlock;
		private Display mDisplay;

		public Encoder (Display display) {
			resize (display);
		}

		public void resize(Display display) {
			mDisplay = display;
			mCrcBlock = new CRC32Block (display);
		}

		public bool IsActive {
			get { return true; }
		}

		public void ProcessEvents(double timeout=0) {
			/*
				cdef unsigned int p = 0
				cdef unsigned int block
				cdef unsigned int crc32
				self.changed.clear()
				start = time.time()
				for block in self.crc32.bitmap:
					crc32 = 0
					p = block * 64
					for i in range(64):
						crc32 = crc32_16bytes(self._fb[p:], 64, crc32)
						p += self.width
						if crc32 == self.crc32[block]:
							continue
							self.crc32[block] = crc32

							self.changed.add(block)
							print(self.changed)
							print('{:.6f}'.format(time.time() - start))
							*/
		}

		public void MarkRectAsModified(int x1, int y1, int x2, int y2) {
			var region = new Region (x1, y1, x2, y2);

			mCrcBlock.MarkRegion(r);
		}
	}
}

