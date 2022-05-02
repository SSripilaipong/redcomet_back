from typing import Callable, Any

from redcomet.base.actor.message import MessageAbstract
from redcomet.base.discovery.ref import ActorDiscoveryRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messaging.handler import PacketHandlerAbstract
from redcomet.base.messaging.packet import Packet
from redcomet.messenger.factory import create_messenger
from redcomet.messenger.request import MessageForwardRequest


class DummyMessage(MessageAbstract):
    def __init__(self, value):
        self.value = value


class MockPacketHandler(PacketHandlerAbstract):
    def __init__(self):
        self.received_packet = None

    def handle(self, packet: Packet):
        self.received_packet = packet


class DummyQueryAddressResponse(MessageAbstract):
    pass


class MockActorDiscoveryRef(ActorDiscoveryRefAbstract):
    def __init__(self, query_response_params=None):
        self._query_response_params = query_response_params
        self.queried_address = None

    def register_address(self, target: str, node_id: str):
        pass

    def query_address(self, target: str, requester_node_id: str, requester_target: str):
        self.queried_address = target, requester_node_id, requester_target

    def call_on_query_address_response(self, message: MessageAbstract, func: Callable[[str, Address], Any]) -> bool:
        if self._query_response_params:
            func(*self._query_response_params)
            return True
        return False


def _create_messenger_with_node_id(handler: PacketHandlerAbstract, node_id: str):
    messenger = create_messenger(handler, actor_id="messenger")
    messenger.assign_node_id(node_id)
    return messenger


def test_should_forward_message_to_be_process_later():
    handler = MockPacketHandler()
    me = _create_messenger_with_node_id(handler, "me")

    me.send(DummyMessage(123), "mine", "yours")

    content = handler.received_packet.content
    assert isinstance(content, MessageForwardRequest) and content.message.value == 123


def test_should_send_query_message_to_discovery_when_address_is_unknown():
    discovery = MockActorDiscoveryRef()
    me = _create_messenger_with_node_id(..., "me")
    me.bind_discovery(discovery)
    me.receive(MessageForwardRequest(DummyMessage(123), "mine", "yours"), ..., ..., ...)
    assert discovery.queried_address == ("yours", "me", "messenger")


def test_should_forward_message_to_queried_address():
    your_handler = MockPacketHandler()
    me = _create_messenger_with_node_id(..., "me")
    you = _create_messenger_with_node_id(your_handler, "you")
    me.make_connection_to(you)
    me.bind_discovery(MockActorDiscoveryRef(query_response_params=("yours", Address("you", "yours"))))

    me.receive(MessageForwardRequest(DummyMessage(123), "mine", "yours"), ..., ..., ...)
    me.receive(DummyQueryAddressResponse(), ..., ..., ...)

    assert your_handler.received_packet.content.value == 123


def test_should_not_forward_message_when_queried_address_is_empty():
    your_handler = MockPacketHandler()
    my_handler = MockPacketHandler()
    me = _create_messenger_with_node_id(my_handler, "me")
    you = _create_messenger_with_node_id(your_handler, "you")
    me.make_connection_to(you)
    me.bind_discovery(MockActorDiscoveryRef(query_response_params=("yours", None)))

    me.receive(MessageForwardRequest(DummyMessage(123), "mine", "yours"), ..., ..., ...)
    me.receive(DummyQueryAddressResponse(), ..., ..., ...)

    assert your_handler.received_packet is None
    assert my_handler.received_packet is None