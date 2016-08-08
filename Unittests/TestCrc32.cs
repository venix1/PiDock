using NUnit.Framework;
using System;
// using Crc32C;
using Force.Crc32;

namespace PiDock.Unittests
{
	[TestFixture]
	public class Crc32
	{
		[Test ]
		public void Benchmark ()
		{
			var rnd = new Random ();
			var fb = new byte [1920 * 1080 * 4];
			rnd.NextBytes (fb);

			while (true) {
				// Initialized 1920x1080x4 framebuffer
				var start = DateTime.Now;
				// var crc32 = new Crc32CAlgorithm ();
				var crc32 = new Crc32Algorithm ();
				for (int i = 0; i < 60; ++i)
					crc32.ComputeHash (fb);

				long elapsedTicks = DateTime.Now.Ticks - start.Ticks;
				var elapsedSpan = new TimeSpan (elapsedTicks);

				Console.WriteLine ("   {0:N0} nanoseconds", elapsedTicks * 100);
				Console.WriteLine ("   {0:N0} ticks", elapsedTicks);
				Console.WriteLine ("   {0:N3} seconds", elapsedSpan.TotalSeconds);
				Console.WriteLine ("   {0:N2} minutes", elapsedSpan.TotalMinutes);
				Console.WriteLine ("   {0:N0} days, {1} hours, {2} minutes, {3} seconds",
					elapsedSpan.Days, elapsedSpan.Hours,
					elapsedSpan.Minutes, elapsedSpan.Seconds);
			}
		}
	}
}