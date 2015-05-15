"""
A very simply autopilot designed to simplify testing of planes by providing an
existing framework for getting a plane in the air.
"""

from .io import Protocol
from . import packets


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
            _, _, true_heading, _ = packet.read_pitch_roll_headings()
            diff = self._take_off_heading - true_heading

            print(diff)

            p = packets.DataPacket()
            p.write_joystick_elevator_aileron_rudder(rudder=diff * 3, elevator=0.1)
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
