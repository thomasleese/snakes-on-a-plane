import asyncio

import xplane.autopilot
import xplane.io


class MyProtocol(xplane.io.Protocol, xplane.autopilot.TakeOffMixin):
    def __init__(self, remote_addr):
        super().__init__(remote_addr)

    def got_data_packet(self, packet, address):
        self.take_off_got_data_packet(packet, address)


def mainloop(local_addr, remote_addr, action):
    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(lambda: MyProtocol(remote_addr),
                                            local_addr=local_addr)
    transport, protocol = loop.run_until_complete(connect)

    loop.call_soon(lambda: getattr(protocol, action)())

    loop.run_forever()
    transport.close()
    loop.close()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('send_host', type=str)
    parser.add_argument('--send-port', '-p', type=int, default=49000)
    parser.add_argument('--listen-host', '-b', type=str, default='0.0.0.0')
    parser.add_argument('--listen-port', '-P', type=int, default=49000)
    parser.add_argument('action', type=str, choices=['take_off'])
    args = parser.parse_args()

    local_addr = (args.listen_host, args.listen_port)
    remote_addr = (args.send_host, args.send_port)

    mainloop(local_addr, remote_addr, args.action)
