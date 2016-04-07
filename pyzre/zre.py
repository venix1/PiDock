"""Python implementation of ZRE protocol."""

import asyncio
import socket
import struct
import uuid
import zmq

# ZRE_DISC_GRP = '224.1.1.1'
ZRE_DISC_GRP = '255.255.255.255'
ZRE_DISC_PORT = 5670

# Helper methods for struct module


def get_data(fmt, payload):
    """Extract abritrary fmt from payload."""
    data = struct.unpack_from(fmt, payload)
    del payload[:struct.calcsize(fmt)]
    if len(data) == 1:
        return data[0]
    else:
        return data


def get_string(payload):
    """extract string from length prefixed bytearray."""
    size = payload[0]
    string = payload[1:size+1]
    del payload[:size+1]
    return bytes(string)


def put_string(string):
    """Store string as length prefixed bytearray."""
    assert len(string) < 256
    payload = bytes([len(string)])
    payload += string
    assert len(payload) == len(string)+1

    return payload


class BeaconMsg(object):
    """Python class for ZRE Beacon message."""

    MSG_FORMAT = '!3sB16sH'

    def __init__(self, uuid=None, port=None):
        """constructor."""
        self.uuid = uuid
        self.port = port

    def pack(self):
        """Return packed bytearray."""
        return self.__class__.pack(self.uuid, self.port)

    @classmethod  # noqa. classmethod/static
    def pack(cls, uuid, port):
        """Pack uuid and port into bytearary."""
        return struct.pack(cls.MSG_FORMAT, b'ZRE', 1, uuid.bytes, port)

    @classmethod
    def unpack(cls, payload):
        """Unpack class from payload."""
        header, version, _uuid, port = struct.unpack(cls.MSG_FORMAT, payload)
        assert header == b'ZRE'
        assert version == 1
        return cls(uuid.UUID(bytes=_uuid), port)


class HelloMsg(object):
    """
    Greet a peer so it can connect back to us.

    S:HELLO         = signature %x01 sequence ipaddress mailbox groups status
                      headers
    signature       = %xAA %xA1
    sequence        = 2OCTET        ; Incremental sequence number
    ipaddress       = string        ; Sender IP address
    string          = size *VCHAR
    size            = OCTET
    mailbox         = 2OCTET        ; Sender mailbox port number
    groups          = strings       ; List of groups sender is in
    strings         = size *string
    status          = OCTET         ; Sender group status sequence
    headers         = dictionary    ; Sender header properties
    dictionary      = size *key-value
    key-value       = string        ; Formatted as name=value
    """

    def __init__(self, nonce, ip, mailbox, groups, status, headers):
        """constructor."""
        self.nonce = nonce
        self.ip = ip
        self.mailbox = mailbox
        self.groups = groups
        self.status = status
        self.headers = headers

    @classmethod
    def pack(cls, nonce, ip, mailbox, groups, status, headers):
        """pack payload returning class instance."""
        payload = struct.pack('3B', 0xAA, 0xA1, 0x01)
        payload += struct.pack('B', nonce)
        payload += put_string(ip)
        payload += struct.pack('!H', mailbox)

        payload += struct.pack('B',    len(groups))
        for group in groups:
            payload += put_string(group)

        payload += struct.pack('B', status)

        payload += struct.pack('B', len(headers))
        for key, value in headers:
            payload += put_string(key + '=' + value)

        return payload

    @classmethod
    def unpack(cls, payload):
        """unpack payload return message."""
        assert payload[:3] == b'\xaa\xa1\x01', payload
        payload = bytearray(payload[3:])

        nonce = get_data('B', payload)
        ip = get_string(payload)
        mailbox = get_data('!H', payload)

        groups = []
        size = get_data('B', payload)
        for _ in range(size):
            groups.append(get_string(payload))

        status = get_data('B', payload)

        headers = []
        size = get_data('B', payload)
        for _ in range(size):
            header = get_string(payload)
            key, value = header.split('=', 1)
            headers[key] = value

        return cls(nonce, ip, mailbox, groups, status, headers)


class WhisperMsg(object):
    """
    Send a message to a peer.

    S:WHISPER       = signature %x02 sequence content
    content         = FRAME         ; Message content as 0MQ frame
    """

    def __init__(self, nonce, content):
        """constructor."""
        self.nonce = nonce
        self.content = content

    @classmethod
    def pack(cls, nonce, msg):
        """Pack message into class."""
        payload = struct.pack('3B', 0xAA, 0xA1, 0x02)
        payload += struct.pack('B', nonce)

        return [payload, msg]

    @classmethod
    def unpack(cls, payload):
        """Unpack message from bytearray."""
        assert payload[:3] == b'\xaa\xa1\x02', payload
        payload = bytearray(payload[3:])

        nonce = get_data('B', payload)

        return cls(nonce, bytes(payload))


class ZREPeer(object):
    """Python representation of ZRE Peer."""

    def __init__(self, uuid, addr, identity):
        """constructor."""
        self.uuid = uuid
        self.addr = addr
        self.nonce = 0
        # self.last = time.now()
        # self.status = 0
        # self.groups = []
        # self.headers = {}

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.bytes)
        print(identity, 'tcp://%s:%s' % self.addr)
        self.socket.connect('tcp://%s:%s' % self.addr)


class ZRE(object):
    """
    Python ZRE implementation.

    http://rfc.zeromq.org/spec:20
    """

    def __init__(self, flags=0, _uuid=None, loop=None):
        """Constructor."""
        self.peers = {}
        self.groups = []
        self.status = 0
        self.headers = {}
        self.ip = None

        if not _uuid:
            self.uuid = uuid.uuid4()

        self.listen()

    def listen(self):
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

    # def broadcast(self):
    #   """configure beacon broadcast loop."""
    #   # configure beacon timer
    #   loop = asyncio.get_event_loop()
    #   loop.call_later(1, self.broadcast)

    def add_peer(self, uuid, addr):
        """Add a peer."""
        peer = ZREPeer(uuid, addr, self.uuid)
        self.peers[uuid.int] = peer

        self.hello(peer)

        return peer

    @asyncio.coroutine
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

    def broadcast(self):
        """Broadcast beacon."""
        # Send payload
        self.beacon_payload = struct.pack('!3sB16sH', b'ZRE', 1,
                                          self.uuid.bytes, self.mailbox)
        self.beacon.sendto(self.beacon_payload, (ZRE_DISC_GRP, ZRE_DISC_PORT))

        # schedule again
        asyncio.get_event_loop().call_later(1, self.broadcast)

    def hello(self, peer):
        """
        Greet a peer so it can connect back to us.

        S:HELLO         = signature %x01 sequence ipaddress mailbox groups
        status headers
        signature       = %xAA %xA1
        sequence        = 2OCTET        ; Incremental sequence number
        ipaddress       = string        ; Sender IP address
        string          = size *VCHAR
        size            = OCTET
        mailbox         = 2OCTET        ; Sender mailbox port number
        groups          = strings       ; List of groups sender is in
        strings         = size *string
        status          = OCTET         ; Sender group status sequence
        headers         = dictionary    ; Sender header properties
        dictionary      = size *key-value
        key-value       = string        ; Formatted as name=value
        """
        msg = HelloMsg.pack(peer.nonce, self.ip, self.mailbox,
                            self.groups, self.status, self.headers)
        peer.socket.send(msg)

    def whisper(self, peer, msg):
        """
        Send a message to a peer.

        S:WHISPER       = signature %x02 sequence content
        content         = FRAME         ; Message content as 0MQ frame
        """
        payload = WhisperMsg.pack(peer.nonce, msg)
        peer.socket.send_multipart(payload)

    def shout(self):
        """
        Send a message to a group.

        S:SHOUT         = signature %x03 sequence group content
        group           = string        ; Name of group
        content         = FRAME         ; Message content as 0MQ frame
        """
        pass

    def join(self):
        """
        Join a group.

        S:JOIN          = signature %x04 sequence group status
        status          = OCTET         ; Sender group status sequence
        """
        pass

    def leave(self):
        """
        Leave a group.

        S:LEAVE         = signature %x05 sequence group status
        """
        pass

    def ping(self):
        """
        Ping a peer that has gone silent.

        S:PING          = signature %06 sequence
        """
        pass

    def pong(self):
        """
        Reply to a peer's ping.

        R:PING-OK       = signature %07 sequence
        """
        pass
