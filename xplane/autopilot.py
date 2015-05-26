"""
A very simple autopilot designed to simplify testing of planes by providing an
existing framework for getting a plane in the air.
"""

from . import packets
from .io import Protocol
from .packets import units


class TakeOffMixin:
    _take_off_state = None
    _take_off_heading = None

    def take_off(self):
        self.take_off_started()

    def take_off_got_data_packet(self, packet, address):
        if self._take_off_state is None:
            return False

        if self._take_off_state == 'started':
            _, _, true_heading, _ = packet.read_pitch_roll_headings()
            self._take_off_heading = true_heading
            print('Landing strip heading is:', true_heading)
            self._take_off_throttle()
            self._take_off_state = 'throttle'
        elif self._take_off_state == 'throttle':
            _, roll, true_heading, _ = packet.read_pitch_roll_headings()
            lift, _, _ = packet.read_aero_forces()

            rudder = (self._take_off_heading - true_heading) * 5
            elevator = 0
            aileron = 0

            # TODO calculate this based on weight of craft
            if lift >= 5000 * units.newton:
                elevator = 0.25
                aileron = -roll.to(units.radians).magnitude

            p = packets.DataPacket()
            p.write_joystick_elevator_aileron_rudder(rudder=rudder,
                                                     aileron=aileron,
                                                     elevator=elevator)
            self.send_packet(p)

        return True

    def _take_off_throttle(self):
        self.send_packet(packets.CommandPacket('sim/flight_controls/brakes_toggle_regular'))

        packet = packets.DataPacket()
        packet.write_throttle_command(1)
        self.send_packet(packet)

    def take_off_started(self):
        self._take_off_state = 'started'

    def take_off_finished(self):
        self._take_off_state = None
