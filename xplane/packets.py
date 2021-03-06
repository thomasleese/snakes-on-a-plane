"""A set of classes for reading and writing packets from X-Plane."""

import socket
import struct

import pint


units = pint.UnitRegistry()


GRAVITY = 9.81 * (units.meter / units.second ** 2)
LEAVE_ALONE = -999


class DataPacket:
    """
    Contains methods for reading data from a 'DATA' packet.

    Parameters
    ----------
    data : bytes
        The raw bytes in the packet, passed to :func:`.read`.
    """

    def __init__(self, data=None):
        self.data = {}

        if data is not None:
            self.read(data)

    def read(self, data):
        """
        Parse the data in the packet and read it into this class.

        Parameters
        ----------
        data : bytes
            The raw bytes in the packet.
        """

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
        """
        Write the contents of this packet to a byte string suitable for sending
        back to X-Plane.

        Returns
        -------
        bytes
            The array of bytes.
        """

        data = b''

        for index, values in self.data.items():
            data += struct.pack('<i', index)

            assert len(values) == 8

            for value in values:
                data += struct.pack('<f', value)

        assert len(data) == len(self.data) * 36

        return b'DATA\x00' + data

    def __getitem__(self, index):
        """
        Get the 8-valued tuple for the specific index.

        Returns
        -------
        tuple
            A tuple of length 8 containing floats.

        Raises
        ------
        IndexError
            If said index is not in the data.
        """

        try:
            return self.data[index]
        except KeyError:
            raise IndexError('Packet does not contain index {}.'.format(index))

    def __setitem__(self, index, values):
        """
        Set the 8-valued tuple for the specific index.

        Parameters
        ----------
        index : int
            The index of the values.
        values : tuple
            The 8 floats for this index.

        Raises
        ------
        ValueError
            If the tuple doesn't contain exactly 8 values.
        """

        if len(values) != 8:
            raise ValueError('Tried to set values of length {}, should be 8.'
                             .format(len(values)))
        self.data[index] = values

    def read_speeds(self):
        """
        Read the speeds (index 3).

        Returns
        -------
        Indicated Airspeed : m/s
        Equivalent Airspeed : m/s
        True Airspeed : m/s
        Groundspeed : m/s
        """

        values = self[3]

        meters_per_second = units.meter / units.second

        indicated_airspeed = (values[0] * units.knot).to(meters_per_second)
        equivalent_airspeed = (values[1] * units.knot).to(meters_per_second)
        true_airspeed = (values[2] * units.knot).to(meters_per_second)
        groundspeed = (values[3] * units.knot).to(meters_per_second)

        return indicated_airspeed, equivalent_airspeed, true_airspeed, \
            groundspeed

    def write_joystick_elevator_aileron_rudder(self, elevator=LEAVE_ALONE,
                                               aileron=LEAVE_ALONE,
                                               rudder=LEAVE_ALONE):
        self[8] = (elevator, aileron, rudder) + (0,) * 5

    def read_angular_moments(self):
        """
        Read the angular moments (index 15).

        Returns
        -------
        L : Nm
        M : Nm
        N : Nm
        """

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

    def read_gear_break(self):
        """
        Read the gear and breaks (index 16).

        Returns
        -------
        Gear : float
        W-break : float
        L-break : float
        R-break : float
        """

        values = self[16]

        gear = values[0]
        wbrak = values[1]
        lbrak = values[2]
        rbrak = values[3]

        return gear, wbrak, lbrak, rbrak

    def write_gear_break(self, gear=LEAVE_ALONE, wbrak=LEAVE_ALONE,
                         lbrak=LEAVE_ALONE, rbrak=LEAVE_ALONE):
        """
        Write the gear and breaks (index 16).

        Parameters
        -------
        gear : float
        wbrak : float
        lbrak : float
        rbrak : float
        """

        self[16] = (gear, wbrak, lbrak, rbrak) + (0,) * 4

    def read_angular_velocities(self):
        """
        Read the angular velocities (index 16).

        Returns
        -------
        P : rad/s
        Q : rad/s
        R : rad/s
        """

        values = self[16]

        radians_per_second = units.radian / units.second

        Q = values[0] * radians_per_second
        P = values[1] * radians_per_second
        R = values[2] * radians_per_second

        return P, Q, R

    def read_pitch_roll_headings(self):
        """
        Read the pitch, roll and headings (index 17).

        Returns
        -------
        Pitch : rad
        Roll : rad
        True Heading : rad
        Magnetic Heading : rad
        """

        values = self[17]

        pitch = (values[0] * units.degree).to(units.radian)
        roll = (values[1] * units.degree).to(units.radian)
        true_heading = (values[2] * units.degree).to(units.radian)
        magnetic_heading = (values[2] * units.degree).to(units.radian)

        return pitch, roll, true_heading, magnetic_heading

    def read_latitude_longitude_altitude(self):
        """
        Read the latitude, longitude and altitude (index 20).

        Returns
        -------
        Latitde : rad
        Longitude : rad
        Mean Sea Level Altitude : m
        Above Ground Level Altitude : m
        """

        values = self[20]

        latitude = (values[0] * units.degree).to(units.radian)
        longitude = (values[1] * units.degree).to(units.radian)
        mean_sea_level_altitude = (values[2] * units.feet).to(units.meter)
        above_ground_level_altitude = (values[4] * units.feet).to(units.meter)

        return latitude, longitude, mean_sea_level_altitude, \
            above_ground_level_altitude

        def read_angle_of_attack_side_slip_paths(self):
            """
            Read the angle of attack, side slip and paths (index 18).

            Returns
            -------
            Alpha : rad
            Beta : rad
            H-path : rad
            V-path : rad
            Slip : rad
            """

            values = self[18]

            alpha = (values[0] * units.degree).to(units.radian)
            beta = (values[1] * units.degree).to(units.radian)
            hpath = (values[2] * units.degree).to(units.radian)
            vpath = (values[3] * units.degree).to(units.radian)
            slip = (values[4] * units.degree).to(units.radian)

            return alpha, beta, hpath, vpath, slip

    def write_throttle_command(self, value):
        """
        Write a throttle command.

        Parameters
        ----------
        value : float
            The value of the throttle.
        """

        self[25] = (value,) + (0,) * 7

    def read_engine_thrust(self):
        """
        Read the engine thrust (index 35).

        Returns
        -------
        Engine Thrust : N
        """

        values = self[35]

        v = ((values[0] * units.lb).to(units.kg) * GRAVITY).to(units.newton)

        return v

    def read_aero_forces(self):
        """
        Read the aero forces (index 64).

        Returns
        -------
        Lift : N
        Drag : N
        Side : N
        """

        values = self[64]

        lift = ((values[0] * units.lb).to(units.kg) * GRAVITY).to(units.newton)
        drag = ((values[1] * units.lb).to(units.kg) * GRAVITY).to(units.newton)
        side = ((values[2] * units.lb).to(units.kg) * GRAVITY).to(units.newton)

        return lift, drag, side

    def read_aileron_angle(self):
        """
        Read the aileron angle (index 70).

        Returns
        -------
        1 : (rad, rad)
        2 : (rad, rad)
        3 : (rad, rad)
        4 : (rad, rad)
        """

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
        """
        Read the elevator angle (index 74).

        Returns
        -------
        1 : (rad, rad)
        2 : (rad, rad)
        """

        values = self[74]

        elev1_1 = (values[0] * units.degree).to(units.radian)
        elev1_2 = (values[1] * units.degree).to(units.radian)
        elev2_1 = (values[2] * units.degree).to(units.radian)
        elev2_2 = (values[3] * units.degree).to(units.radian)

        return (elev1_1, elev1_2), (elev2_1, elev2_2)

    def read_rudder_angle(self):
        """
        Read the rudder angle (index 75).

        Returns
        -------
        1 : (rad, rad)
        2 : (rad, rad)
        """

        values = self[75]

        rudd1_1 = (values[0] * units.degree).to(units.radian)
        rudd1_2 = (values[1] * units.degree).to(units.radian)
        rudd2_1 = (values[2] * units.degree).to(units.radian)
        rudd2_2 = (values[3] * units.degree).to(units.radian)

        return (rudd1_1, rudd1_2), (rudd2_1, rudd2_2)


class CommandPacket:
    def __init__(self, command=None, data=None):
        self.command = command

        if data is not None:
            self.read(data)

    def read(self, data):
        if not data.startswith(b'CMND'):
            raise ValueError("Not a 'DATA' packet.")

        data = data[5:]

        self.command = data.decode()

    def write(self):
        return b'CMND0' + self.command.encode()
