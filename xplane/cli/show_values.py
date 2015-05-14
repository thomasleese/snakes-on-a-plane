import asyncio
import curses
import socket

import xplane.io


class MyProtocol(xplane.io.Protocol):
    def __init__(self, window):
        self.window = window

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def show_value(self, y, x, name, value, d=2):
        self.window.addstr(y, x, name, curses.color_pair(2))
        self.window.addstr(y, x + len(name) + 1, str(round(value, d)), curses.color_pair(1))

    def got_data_packet(self, packet, address):
        # Parse all the values.

        self.window.clear()

        try:
            _, _, true_airspeed, _ = packet.read_speeds()
            self.show_value(1, 1, 'Speed', true_airspeed)
        except IndexError:
            pass

        try:
            L, M, N = packet.read_angular_moments()
            self.show_value(3, 1, 'M', M)
            self.show_value(3, 31, 'L', L)
            self.show_value(3, 61, 'N', N)
        except IndexError:
            pass

        try:
            P, Q, R = packet.read_angular_velocities()
            self.show_value(5, 1, 'P', P)
            self.show_value(5, 31, 'Q', Q)
            self.show_value(5, 61, 'R', R)
        except IndexError:
            pass

        try:
            pitch, roll, yaw = packet.read_pitch_roll_yaw()
            self.show_value(7, 1, 'Pitch', pitch)
            self.show_value(7, 31, 'Roll', roll)
            self.show_value(7, 61, 'Yaw', yaw)
        except IndexError:
            pass

        try:
            engine_thrust = packet.read_engine_thrust()
            self.show_value(9, 1, 'Engine Thrust', engine_thrust)
        except IndexError:
            pass

        try:
            lift, drag, side = packet.read_aero_forces()
            self.show_value(11, 1, 'Lift', lift)
            self.show_value(11, 31, 'Drag', drag)
            self.show_value(11, 61, 'Side', side)
        except IndexError:
            pass

        try:
            aileron1, aileron2, aileron3, aileron4 = packet.read_aileron_angle()
            self.show_value(13, 1, 'Aileron #1 Left', aileron1[0], d=4)
            self.show_value(14, 1, 'Aileron #2 Left', aileron2[0], d=4)
            self.show_value(15, 1, 'Aileron #3 Left', aileron3[0], d=4)
            self.show_value(16, 1, 'Aileron #4 Left', aileron4[0], d=4)
            self.show_value(13, 36, 'Aileron #1 Right', aileron1[1], d=4)
            self.show_value(14, 36, 'Aileron #2 Right', aileron2[1], d=4)
            self.show_value(15, 36, 'Aileron #3 Right', aileron3[1], d=4)
            self.show_value(16, 36, 'Aileron #4 Right', aileron4[1], d=4)
        except IndexError:
            pass

        try:
            elevator1, elevator2 = packet.read_elevator_angle()
            self.show_value(18, 1, 'Elevator #1 Left', elevator1[0], d=4)
            self.show_value(19, 1, 'Elevator #2 Left', elevator2[0], d=4)
            self.show_value(18, 36, 'Elevator #1 Right', elevator1[1], d=4)
            self.show_value(19, 36, 'Elevator #2 Right', elevator2[1], d=4)
        except IndexError:
            pass

        try:
            rudder1, rudder2 = packet.read_rudder_angle()
            self.show_value(21, 1, 'Rudder #1 Left', rudder1[0], d=4)
            self.show_value(22, 1, 'Rudder #2 Left', rudder2[0], d=4)
            self.show_value(21, 36, 'Rudder #1 Right', rudder1[1], d=4)
            self.show_value(22, 36, 'Rudder #2 Right', rudder2[1], d=4)
        except IndexError:
            pass

        self.window.refresh()


def mainloop(window, address):
    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(lambda: MyProtocol(window),
                                            local_addr=address)
    transport, protocol = loop.run_until_complete(connect)
    loop.run_forever()
    transport.close()
    loop.close()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-b', '--bind', type=str, default='::')
    parser.add_argument('-p', '--port', type=int, default=49000)
    args = parser.parse_args()

    curses.wrapper(mainloop, (args.bind, args.port))


if __name__ == '__main__':
    main()
