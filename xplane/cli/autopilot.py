import xplane.autopilot


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('send-host', type=str)
    parser.add_argument('--send-port', '-p', type=int, default=49000)
    parser.add_argument('--receive-host', '-b', type=str, default='::')
    parser.add_argument('--receive-port', '-P', type=int, default=49000)
    parser.add_argument('action', type=str)
    args = parser.parse_args()

    try:
        action_func = getattr(xplane.autopilot, args.action)
    except AttributeError:
        print('No such autopilot action: {}.'.format(args.action))
    else:
        action_func()
