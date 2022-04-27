from typing import List, Tuple

from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.discovery import ActorDiscovery
from redcomet.base.messaging.address import Address
from redcomet.base.messaging.inbox import Inbox
from redcomet.base.messaging.outbox import Outbox
from redcomet.base.messaging.packet import Packet
from redcomet.base.node import NodeAbstract
from redcomet.cluster.manager import ClusterManager
from redcomet.cluster.ref import ClusterRef
from redcomet.messenger import Messenger
from redcomet.node.register import RegisterActorRequest
from redcomet.queue.abstract import QueueAbstract
from redcomet.queue.default import DefaultQueue
from redcomet.system.node_factory import create_gateway_node, create_worker_node


class ActorSystem:
    def __init__(self, cluster: ClusterRefAbstract, gateway: NodeAbstract, incoming_messages: QueueAbstract,
                 gateway_messenger: Messenger):
        self._cluster = cluster
        self._gateway = gateway
        self._incoming_messages = incoming_messages
        self._gateway_messenger = gateway_messenger

    @classmethod
    def create(cls) -> 'ActorSystem':
        incoming_messages = DefaultQueue()

        discovery = ActorDiscovery.create("discovery", "main")

        gateway, gateway_inbox, gateway_outbox, gateway_messenger \
            = create_gateway_node("main", incoming_messages, discovery)
        discovery.set_outbox(gateway_outbox)

        node0, inbox0, outbox0 = create_worker_node("node0", discovery)

        _wire_outboxes_to_inboxes([("main", gateway_inbox), ("node0", inbox0)], [gateway_outbox, outbox0])

        cluster = ClusterManager(gateway_messenger, "cluster")
        cluster.add_node(node0, "node0")
        _register_cluster(cluster, gateway_messenger)
        return cls(ClusterRef(gateway_messenger, "main"), gateway, incoming_messages, gateway_messenger)

    def spawn(self, actor: ActorAbstract) -> ActorRefAbstract:
        return self._cluster.spawn(actor)

    def __enter__(self) -> 'ActorSystem':
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def fetch_message(self, timeout: float = None) -> MessageAbstract:
        return self._incoming_messages.get(timeout=timeout)

    def start(self):
        pass

    def stop(self):
        pass


def _wire_outboxes_to_inboxes(inboxes: List[Tuple[str, Inbox]], outboxes: List[Outbox]):
    for outbox in outboxes:
        for name, inbox in inboxes:
            outbox.register_inbox(inbox, name)


def _register_cluster(cluster: ClusterManager, messenger: Messenger):
    content = RegisterActorRequest("cluster", cluster)
    packet = Packet(content, Address.on_local("main"), Address.on_local("manager"))
    messenger.send_packet(packet)