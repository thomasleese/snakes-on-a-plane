import socket
import struct

import pint


units = pint.UnitRegistry()


GRAVITY = 9.81 * (units.meter / units.second ** 2)
LEAVE_ALONE = -999


class DataPacket:
    """
    Contains methods for reading data from a 'DATA' packet.
    """

    def __init__(self, data=None):
        self.data = {}

        if data is not None:
            self.read(data)

    def read(self, data):
        if not data.startswith(b'DATA'):
            raise ValueError("Not a 'DATA' packet.")

        data = data[5:]

        for i in range(len(data) // 36):
            index = struct.unpack_from('<i', data, 0 + (i * 36))[0]

            values = []
            for j in range(8):
                value = struct.unpack_from('<f', data, 4 + (i * 36) + (j * 4))[0]
                values.append(value)

            self.data[index] = values

    def write(self):
        data = b''

        for index, values in self.data.items():
            data += struct.pack('<i', index)

            assert len(values) == 8

            for value in values:
                data += struct.pack('<f', value)

        assert len(data) == len(self.data) * 36

        return b'DATA\x00' + data

    def __getitem__(self, key):
        try:
            return self.data[key]
        except IndexError:
            raise IndexError('Packet does not contain index {}.'.format(key))

    def __setitem__(self, index, values):
        if len(values) != 8:
            raise ValueError('Tried to set values of length {}, should be 8.'
                             .format(len(values)))
        self.data[index] = values

    def read_speeds(self):
        values = self[3]

        meters_per_second = units.meter / units.second

        indicated_airspeed = (values[0] * units.knot).to(meters_per_second)
        equivalent_airspeed = (values[1] * units.knot).to(meters_per_second)
        true_airspeed = (values[2] * units.knot).to(meters_per_second)
        groundspeed = (values[3] * units.knot).to(meters_per_second)

        return indicated_airspeed, equivalent_airspeed, true_airspeed, \
            groundspeed

    def read_angular_moments(self):
        values = self[15]

        newton_meters = units.newton * units.meter

        """
        M = values[0] * (units.foot * units.pound).to(newton_meters)
        L = values[1] * (units.foot * units.pound).to(newton_meters)
        N = values[2] * (units.foot * units.pound).to(newton_meters)
        """

        M = (values[0] * 1.35581795) * newton_meters
        L = (values[1] * 1.35581795) * newton_meters
        N = (values[2] * 1.35581795) * newton_meters

        return L, M, N

    def read_angular_velocities(self):
        values = self[16]

        radians_per_second = units.radian / units.second

        Q = values[0] * radians_per_second
        P = values[1] * radians_per_second
        R = values[2] * radians_per_second

        return P, Q, R

    def read_pitch_roll_yaw(self):
        values = self[17]

        pitch = (values[0] * units.degree).to(units.radian)
        roll = (values[1] * units.degree).to(units.radian)
        yaw = (values[2] * units.degree).to(units.radian)

        return pitch, roll, yaw

    def read_angle_of_attack_side_slip_paths(self):
        values = self[18]

        alpha = (values[0] * units.degree).to(units.radian)
        beta = (values[1] * units.degree).to(units.radian)
        hpath = (values[2] * units.degree).to(units.radian)
        vpath = (values[3] * units.degree).to(units.radian)
        slip = (values[4] * units.degree).to(units.radian)

        return alpha, beta, hpath, vpath, slip

    def write_throttle_command(self, value):
        self[25] = (value,) + (0,) * 7

    def read_engine_thrust(self):
        values = self[35]

        v = ((values[0] * units.lb).to(units.kg) * GRAVITY).to(units.newton)

        return v

    def read_aero_forces(self):
        values = self[64]

        lift = ((values[0] * units.lb).to(units.kg) * GRAVITY).to(units.newton)
        drag = ((values[1] * units.lb).to(units.kg) * GRAVITY).to(units.newton)
        side = ((values[2] * units.lb).to(units.kg) * GRAVITY).to(units.newton)

        return lift, drag, side

    def read_aileron_angle(self):
        values = self[70]

        left_1 = (values[0] * units.degree).to(units.radian)
        right_1 = (values[1] * units.degree).to(units.radian)
        left_2 = (values[2] * units.degree).to(units.radian)
        right_2 = (values[3] * units.degree).to(units.radian)
        left_3 = (values[4] * units.degree).to(units.radian)
        right_3 = (values[5] * units.degree).to(units.radian)
        left_4 = (values[6] * units.degree).to(units.radian)
        right_4 = (values[7] * units.degree).to(units.radian)

        return (left_1, right_1), (left_2, right_2), (left_3, right_3), \
            (left_4, right_4)

    def read_elevator_angle(self):
        values = self[74]

        elev1_1 = (values[0] * units.degree).to(units.radian)
        elev1_2 = (values[1] * units.degree).to(units.radian)
        elev2_1 = (values[2] * units.degree).to(units.radian)
        elev2_2 = (values[3] * units.degree).to(units.radian)

        return (elev1_1, elev1_2), (elev2_1, elev2_2)

    def read_rudder_angle(self):
        values = self[75]

        rudd1_1 = (values[0] * units.degree).to(units.radian)
        rudd1_2 = (values[1] * units.degree).to(units.radian)
        rudd2_1 = (values[2] * units.degree).to(units.radian)
        rudd2_2 = (values[3] * units.degree).to(units.radian)

        return (rudd1_1, rudd1_2), (rudd2_1, rudd2_2)
