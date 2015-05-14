def parse_packet(data):
    """
    Parse a packet from X-Plane.

    Parameters
    ----------
    data : bytes
        The raw data in the packet.
    """

    message_type = data[:4]
    index_byte = data[4]
    message = data[5:]
    return message_type, index_byte, message
