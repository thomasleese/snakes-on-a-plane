import curses
import socket

import xplane


def show_value(window, y, x, name, value, d=2):
    window.addstr(y, x, name, curses.color_pair(2))
    window.addstr(y, x + len(name) + 1, str(round(value, d)), curses.color_pair(1))


def got_packet(window, packet):
    message_type, index_byte, message = xplane.io.parse_packet(packet)
    if message_type != b'DATA':
        return  # We don't care what it is.

    data = xplane.packets.DataPacket(message)

    # Parse all the values.
    indicated_airspeed, equivalent_airspeed, true_airspeed, groundspeed = data.read_speeds()
    L, M, N = data.read_angular_moments()
    P, Q, R = data.read_angular_velocities()
    pitch, roll, yaw = data.read_pitch_roll_yaw()
    engine_thrust = data.read_engine_thrust()
    lift, drag, side = data.read_aero_forces()
    aileron1, aileron2, aileron3, aileron4 = data.read_aileron_angle()
    elevator1, elevator2 = data.read_elevator_angle()
    rudder1, rudder2 = data.read_rudder_angle()

    window.clear()

    show_value(window, 1, 1, 'Speed', true_airspeed)

    show_value(window, 3, 1, 'M', M)
    show_value(window, 3, 31, 'L', L)
    show_value(window, 3, 61, 'N', N)

    show_value(window, 5, 1, 'P', P)
    show_value(window, 5, 31, 'Q', Q)
    show_value(window, 5, 61, 'R', R)

    show_value(window, 7, 1, 'Pitch', pitch)
    show_value(window, 7, 31, 'Roll', roll)
    show_value(window, 7, 61, 'Yaw', yaw)

    show_value(window, 9, 1, 'Engine Thrust', engine_thrust)

    show_value(window, 11, 1, 'Lift', lift)
    show_value(window, 11, 31, 'Drag', drag)
    show_value(window, 11, 61, 'Side', side)

    show_value(window, 13, 1, 'Aileron #1 Left', aileron1[0], d=4)
    show_value(window, 14, 1, 'Aileron #2 Left', aileron2[0], d=4)
    show_value(window, 15, 1, 'Aileron #3 Left', aileron3[0], d=4)
    show_value(window, 16, 1, 'Aileron #4 Left', aileron4[0], d=4)
    show_value(window, 13, 36, 'Aileron #1 Right', aileron1[1], d=4)
    show_value(window, 14, 36, 'Aileron #2 Right', aileron2[1], d=4)
    show_value(window, 15, 36, 'Aileron #3 Right', aileron3[1], d=4)
    show_value(window, 16, 36, 'Aileron #4 Right', aileron4[1], d=4)

    show_value(window, 18, 1, 'Elevator #1 Left', elevator1[0], d=4)
    show_value(window, 19, 1, 'Elevator #2 Left', elevator2[0], d=4)
    show_value(window, 18, 36, 'Elevator #1 Right', elevator1[1], d=4)
    show_value(window, 19, 36, 'Elevator #2 Right', elevator2[1], d=4)

    show_value(window, 21, 1, 'Rudder #1 Left', rudder1[0], d=4)
    show_value(window, 22, 1, 'Rudder #2 Left', rudder2[0], d=4)
    show_value(window, 21, 36, 'Rudder #1 Right', rudder1[1], d=4)
    show_value(window, 22, 36, 'Rudder #2 Right', rudder2[1], d=4)

    window.refresh()


def mainloop(window, address):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # Create a socket and connect it to X-Plane.
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind(address)

    # Read and parse packets from X-Plane.
    while True:
        data, addr = sock.recvfrom(1024)
        got_packet(window, data)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-b', '--bind', type=str, default='::')
    parser.add_argument('-p', '--port', type=int, default=49000)
    args = parser.parse_args()

    curses.wrapper(mainloop, (args.bind, args.port))


if __name__ == '__main__':
    main()
