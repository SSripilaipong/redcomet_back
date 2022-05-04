from typing import Optional

from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messenger.abstract import MessengerAbstract
from redcomet.base.node.abstract import NodeAbstract
from redcomet.discovery.ref import ActorDiscoveryRef
from redcomet.node.manager.abstract import NodeManagerAbstract
from redcomet.node.ref import NodeRef


class ProcessNode(NodeAbstract):
    def __init__(self, messenger: MessengerAbstract):
        self._messenger = messenger

        self._manager: Optional[NodeManagerAbstract] = None
        self._actor_id: Optional[str] = None
        self._node_id: Optional[str] = None

    def bind_discovery(self, address: Address):
        ref = ActorDiscoveryRef(self._messenger, address, self._actor_id)
        self._messenger.bind_discovery(ref)
        self._manager.bind_discovery(ref)

    def issue_actor_ref(self, local_issuer_id: str, address: Address) -> ActorRefAbstract:
        pass

    def issue_cluster_ref(self, local_issuer_id: str) -> ClusterRefAbstract:
        pass

    def issue_node_ref(self, local_issuer_id: str, node_id: str) -> NodeRef:
        pass

    def register_executable_actor(self, actor: ActorAbstract, actor_id: str):
        pass

    def assign_node_id(self, node_id: str):
        self._node_id = node_id
        self._actor_id = node_id

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def messenger(self) -> MessengerAbstract:
        return self._messenger

    def make_connection_to(self, node: 'NodeAbstract'):
        pass

    def assign_manager(self, manager: NodeManagerAbstract):
        self._manager = manager