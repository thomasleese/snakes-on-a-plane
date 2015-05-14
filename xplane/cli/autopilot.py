import xplane.autopilot


class MyProtocol(xplane.io.Protocol):
    def __init__(self, action):
        self.action = action


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('send-host', type=str)
    parser.add_argument('--send-port', '-p', type=int, default=49000)
    parser.add_argument('--listen-host', '-b', type=str, default='::')
    parser.add_argument('--listen-port', '-P', type=int, default=49000)
    parser.add_argument('action', type=str)
    args = parser.parse_args()

    try:
        action_func = getattr(xplane.autopilot, args.action)
    except AttributeError:
        print('No such autopilot action: {}.'.format(args.action))
        return

    loop = asyncio.get_event_loop()

    connect = loop.create_datagram_endpoint(lambda: MyProtocol(action_func),
                                            local_addr=(args.listen_host, args.listen_port),
                                            remote_addr=(args.send_host, args.send_port))
    transport, protocol = loop.run_until_complete(connect)

    loop.run_forever()
    transport.close()
    loop.close()
