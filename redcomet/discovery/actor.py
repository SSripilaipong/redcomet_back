from typing import Dict

from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messaging.packet import Packet
from redcomet.base.messenger.abstract import MessengerAbstract
from redcomet.base.node.abstract import NodeAbstract
from redcomet.discovery.message.query.request import QueryAddressRequest
from redcomet.discovery.message.query.response import QueryAddressResponse
from redcomet.discovery.message.register.request import RegisterAddressRequest


class ActorDiscovery(ActorAbstract):
    def __init__(self, address: Address, messenger: MessengerAbstract = None):
        self._address = address
        self._messenger = messenger

        self._mapper: Dict[str, str] = {}

    @classmethod
    def create(cls, actor_id: str, node_id: str) -> 'ActorDiscovery':
        discovery = cls(Address(node_id, actor_id))
        discovery.register_address(node_id, node_id)
        discovery.register_address(actor_id, node_id)
        return discovery

    def set_node(self, node: NodeAbstract):
        self._messenger = node.messenger

    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        if isinstance(message, RegisterAddressRequest):
            self._process_register_request(message)
        elif isinstance(message, QueryAddressRequest):
            self._process_query_address_request(message)
        else:
            raise NotImplementedError()

    def _process_register_request(self, message: RegisterAddressRequest):
        self.register_address(message.target, message.node_id)

    def _process_query_address_request(self, message: QueryAddressRequest):
        node_id = self._query_node_id(message.target)
        address = Address(node_id, message.target)
        packet = Packet(QueryAddressResponse(message.target, address),
                        sender=self._address,
                        receiver=Address(message.requester_node_id, message.requester_target))
        self._messenger.send_packet(packet)

    def register_address(self, target: str, node_id: str):
        if target in self._mapper:
            raise NotImplementedError()
        self._mapper[target] = node_id

    def _query_node_id(self, target: str) -> str:
        print("discovery on", self._address, self._mapper)
        node_id = self._mapper.get(target)
        if node_id is None:
            raise NotImplementedError()
        return node_id

    @property
    def address(self) -> Address:
        return self._address
