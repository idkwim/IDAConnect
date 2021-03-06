# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import logging

from ..shared.packets import Event
from ..shared.sockets import ClientSocket

logger = logging.getLogger('IDAConnect.Network')


class Client(ClientSocket):
    """
    The client (client-side) implementation.
    """

    def __init__(self, plugin, parent=None):
        """
        Initializes the client.

        :param plugin: the plugin instance
        :param parent: the parent object
        """
        ClientSocket.__init__(self, logger, parent)
        self._plugin = plugin

    def disconnect(self, err=None):
        ClientSocket.disconnect(self, err)
        logger.info("Connection lost")

        # Notify the plugin
        self._plugin.notify_disconnected()

    def recv_packet(self, packet):
        if isinstance(packet, Event):
            # Call the event
            self._plugin.core.unhook_all()
            try:
                packet()
            except Exception as e:
                self._logger.warning('Error while calling event')
                self._logger.exception(e)
            self._plugin.core.tick = max(self._plugin.core.tick, packet.tick)
            self._plugin.core.hook_all()
        else:
            return False
        return True

    def send_packet(self, packet):
        if isinstance(packet, Event):
            self._plugin.core.tick += 1
            packet.tick = self._plugin.core.tick
        return ClientSocket.send_packet(self, packet)
