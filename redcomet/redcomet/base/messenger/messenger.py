from redcomet.base.actor import ActorAbstract, ActorRefAbstract
from redcomet.base.actor.discovery import ActorDiscovery
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messaging.outbox import Outbox
from redcomet.base.messaging.packet import Packet
from redcomet.base.messenger.request import MessageForwardRequest


class Messenger(ActorAbstract):
    def __init__(self, node_id: str, outbox: Outbox, discovery: ActorDiscovery):
        self._node_id = node_id
        self._outbox = outbox
        self._discovery = discovery

    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        if isinstance(message, MessageForwardRequest):
            self._forward(message, sender)
        else:
            raise NotImplementedError()

    def _forward(self, message: MessageForwardRequest, sender: ActorRefAbstract):
        sender_node_id = self._get_node_id(sender.ref_id)
        packet = Packet(message,
                        sender=Address(self._node_id, sender.ref_id),
                        receiver=Address(sender_node_id, message.receiver_id))
        self._outbox.send(packet)

    def _get_node_id(self, ref_id: str) -> str:
        return self._discovery.query_node_id(ref_id)
