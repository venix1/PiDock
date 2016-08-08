// http://rfc.zeromq.org/spec:20

using System;

namespace PiDock.Source
{
	// ZRE_DISC_GRP = '255.255.255.255'
	// ZRE_DISC_PORT = 5670

	public class Peer {
	}

	public class ZRE {
		private Peer[] mPeers;

		public ZRE () {
		}

		public void listen() {
			/*
			"""Listen to beacons."""
			# Bind Router
			ctx = zmq.Context.instance()
				self.router = ctx.socket(zmq.ROUTER)
				self.mailbox = self.router.bind_to_random_port('tcp://*')
				print(self.uuid, self.mailbox)

				# Bind Beacon
				self.beacon = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				self.beacon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.beacon.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
				self.beacon.bind(('', ZRE_DISC_PORT))

				# setup asyncio handlers
				loop = asyncio.get_event_loop()
				loop.add_reader(self.beacon, self.beacon_handler, self.beacon)
				loop.create_task(self.router_handler())

				# Get IP address if not configured.
				if not self.ip:
				self.broadcast()
				*/
		}

		public void AddPeer() {
		}

		public void Handler() {
			/*
    def router_handler(self):
        """Router loop."""
        while True:
            events = self.router.poll(0)
            if events:
                msg = self.router.recv_multipart()
                identity = uuid.UUID(bytes=msg[0])
                peer = self.peers.get(identity.int, None)

                # S:HELLO
                if msg[1][:3] == b'\xaa\xa1\x01':
                    msg = HelloMsg.unpack(msg[1])

                    if not peer:
                        # If we don't know our IP, wait for a beacon
                        # Seeing as we got a connection, the beacon
                        # should provide it. This could be spoofed.
                        for attempts in range(10):
                            if not self.ip:
                                yield from asyncio.sleep(0.2)
                            else:
                                break

                        assert self.ip, 'icanhazip?'
                        peer = self.add_peer(identity, (msg.ip.decode('utf-8'),
                                             msg.mailbox))
                    print('S:HELLO')
                    self.on_hello(peer, msg)

                # S:WHISPER
                elif msg[1][:3] == b'\xaa\xa1\x02':
                    msg = WhisperMsg.unpack(msg[1] + msg[2])
                    print('S:WHISPER', msg.content)
                    self.on_whisper(peer, msg)

                else:
                    print('Unknown:', msg)

            yield from asyncio.sleep(0)

*/
		}

		public void BeaconHandler() {
			/*
  def beacon_handler(self, sock):
        """Process beacon."""
        payload, addr = sock.recvfrom(22)
        if len(payload) != 22:
            return

        msg = BeaconMsg.unpack(payload)
        if msg.uuid == self.uuid:
            self.ip = addr[0].encode('utf-8')
            return

        # First retrieve own IP from a beacon
        if not self.ip:
            return

        peer = self.peers.get(msg.uuid.int, None)
        if peer:
            # update idle time
            # TODO: Handle scenario where IP/port changed
            assert addr[0] == peer.addr[0], 'Peer IP changed'
            assert msg.port == peer.addr[1], 'Peer port changed'
            return
        print('Valid Beacon:', addr[0], msg.port)

        # Proceed with greeting
        self.add_peer(msg.uuid, (addr[0], msg.port))

*/
		}

		public void broadcast() {
			/*
    def broadcast(self):
        """Broadcast beacon."""
        # Send payload
        self.beacon_payload = struct.pack('!3sB16sH', b'ZRE', 1,
                                          self.uuid.bytes, self.mailbox)
        self.beacon.sendto(self.beacon_payload, (ZRE_DISC_GRP, ZRE_DISC_PORT))

        # schedule again
        asyncio.get_event_loop().call_later(1, self.broadcast)
*/
	}

		// hello
		// whisper
		// shout
		// join
		// leave
		// ping
		// pong
}

}