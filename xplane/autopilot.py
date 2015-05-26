"""
A very simple autopilot designed to simplify testing of planes by providing an
existing framework for getting a plane in the air.
"""

from . import packets
from .io import Protocol
from .packets import units


class TakeoffMixin:
    _takeoff_state = None
    _takeoff_heading = None

    def takeoff(self):
        self.takeoff_started()

    def takeoff_got_data_packet(self, packet, address):
        if self._takeoff_state is None:
            return False

        if self._takeoff_state == 'started':
            _, _, true_heading, _ = packet.read_pitch_roll_headings()
            self._takeoff_heading = true_heading
            print('Landing strip heading is:', true_heading)
            self._takeoff_throttle()
            self._takeoff_state = 'throttle'
        elif self._takeoff_state == 'throttle':
            _, roll, true_heading, _ = packet.read_pitch_roll_headings()
            lift, _, _ = packet.read_aero_forces()
            _,_, altitude, _ = packet.read_latitude_longitude_altitude()

            rudder = (self._takeoff_heading - true_heading) * 5
            elevator = 0
            aileron = 0

            # TODO calculate this based on weight of craft
            if lift >= 5000 * units.newton:
                elevator = 0.3
                aileron = -roll.to(units.radians).magnitude

            # TODO get this as an argument
            if altitude >= 300 * units.meter:
                elevator = -0.5
                self.takeoff_finished()

            p = packets.DataPacket()
            p.write_joystick_elevator_aileron_rudder(rudder=rudder,
                                                     aileron=aileron,
                                                     elevator=elevator)
            self.send_packet(p)

        return True

    def _takeoff_throttle(self):
        self.send_packet(packets.CommandPacket('sim/flight_controls/brakes_toggle_regular'))

        packet = packets.DataPacket()
        packet.write_throttle_command(1)
        self.send_packet(packet)

    def takeoff_started(self):
        self._takeoff_state = 'started'

    def takeoff_finished(self):
        self._takeoff_state = None
