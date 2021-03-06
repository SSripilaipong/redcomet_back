from abc import ABC, abstractmethod

from redcomet.base.messaging.handler import PacketHandlerAbstract
from redcomet.base.messaging.packet import Packet


class InboxAbstract(ABC):

    @abstractmethod
    def set_handler(self, handler: PacketHandlerAbstract):
        pass

    @abstractmethod
    def receive(self, packet: Packet):
        pass

    def receive_loop(self):
        pass

    def stop_receive_loop(self):
        pass

    def close(self):
        pass
