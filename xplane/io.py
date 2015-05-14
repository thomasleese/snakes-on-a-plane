from . import packets


class Protocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        message_type = data[:4]
        if message_type == b'DATA':
            self.got_data_packet(packets.DataPacket(data))
        else:
            print("Got unknown message type '{}'.".format(message_type))

    def got_data_packet(self, packet, address):
        """
        You should override this.
        """

        pass
