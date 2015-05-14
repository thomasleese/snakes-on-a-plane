"""
A thin layer on top of :mod:`asyncio` for talking with X-Plane over UDP.
"""

from . import packets


class Protocol:
    """The X-Plane UDP protocol."""

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        message_type = data[:4]
        if message_type == b'DATA':
            self.got_data_packet(packets.DataPacket(data), address)
        else:
            print("Got unknown message type '{}'.".format(message_type))

    def got_data_packet(self, packet, address):
        """
        Called when a 'DATA' packet is received.

        This is meant to be override by subclasses; the default implementation
        does nothing.

        Parameters
        ----------
        packet : xplane.packets.DataPacket
            The packet containing the data.
        address : (host, port)
            Who the packet was sent by.
        """

        pass
