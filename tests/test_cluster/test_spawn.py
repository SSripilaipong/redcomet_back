from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.discovery.ref import ActorDiscoveryRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messaging.packet import Packet
from redcomet.base.messenger.abstract import MessengerAbstract
from redcomet.base.messenger.direct_message.ref import DirectMessageBoxRefAbstract
from redcomet.base.node.ref import NodeRefAbstract
from redcomet.cluster.manager import ClusterManager
from redcomet.cluster.message.spawn_actor.request import SpawnActorRequest
from redcomet.cluster.ref import ClusterRef


class MockMessenger(MessengerAbstract):
    def create_direct_message_box(self) -> DirectMessageBoxRefAbstract:
        pass

    def __init__(self):
        self.sent_packet = None

    def send(self, message: MessageAbstract, sender_id: str, receiver_id: str):
        pass

    def send_packet(self, packet: Packet):
        self.sent_packet = packet

    def assign_node_id(self, node_id: str):
        pass

    def bind_discovery(self, ref: ActorDiscoveryRefAbstract):
        pass

    def make_connection_to(self, other: 'MessengerAbstract'):
        pass

    @property
    def node_id(self) -> str:
        return ""


class MockNodeRef(NodeRefAbstract):
    def __init__(self, node_id: str):
        self._node_id = node_id
        self.registered_address = None

    def register_address(self, actor_id: str, actor: ActorAbstract):
        self.registered_address = (actor_id, actor)

    @property
    def node_id(self) -> str:
        return self._node_id


class MyActor(ActorAbstract):
    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        pass


def test_should_send_spawn_message_to_cluster_manager():
    messenger = MockMessenger()
    cluster = ClusterRef(messenger, "me", "main", "cluster")
    my_actor = MyActor()

    cluster.spawn(my_actor)

    packet: Packet = messenger.sent_packet
    content = packet.content
    assert packet.receiver == Address("main", "cluster")
    assert isinstance(content, SpawnActorRequest) and content.actor is my_actor


def test_should_send_register_actor_message_to_node_manager():
    node = MockNodeRef("node0")
    my_actor = MyActor()
    request = SpawnActorRequest(my_actor, "abc")
    cluster = ClusterManager(..., "cluster", ..., node_refs={"node0": node})

    cluster.receive(request, ..., ..., ...)

    assert node.registered_address == ("abc", my_actor)
