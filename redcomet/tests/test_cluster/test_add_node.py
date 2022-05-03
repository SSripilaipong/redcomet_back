from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.base.messenger.abstract import MessengerAbstract
from redcomet.base.node.abstract import NodeAbstract
from redcomet.cluster.manager import ClusterManager
from redcomet.node.ref import NodeRef


class MockNode(NodeAbstract):
    def __init__(self):
        self.assigned_node_id = None
        self.bound_discovery_address = None
        self.connected_nodes = []

    def bind_discovery(self, address: Address):
        self.bound_discovery_address = address

    def issue_actor_ref(self, local_issuer_id: str, ref_id: str) -> ActorRefAbstract:
        pass

    def issue_cluster_ref(self, local_issuer_id: str) -> ClusterRefAbstract:
        pass

    def issue_node_ref(self, local_issuer_id: str, node_id: str) -> NodeRef:
        pass

    def register_executable_actor(self, actor: ActorAbstract, actor_id: str):
        pass

    def assign_node_id(self, node_id: str):
        self.assigned_node_id = node_id

    @property
    def node_id(self) -> str:
        return ...

    @property
    def messenger(self) -> MessengerAbstract:
        return ...

    def make_connection_to(self, node: 'NodeAbstract'):
        self.connected_nodes.append(node)


def test_should_assign_node_id():
    node = MockNode()
    cluster = ClusterManager(MockNode(), "cluster", ...)
    cluster.add_node(node, "abc")
    assert node.assigned_node_id == "abc"


def test_should_bind_node_to_discovery_address():
    node = MockNode()
    cluster = ClusterManager(MockNode(), "cluster", Address("my", "discovery"))
    cluster.add_node(node, "")
    assert node.bound_discovery_address == Address("my", "discovery")


def test_should_connect_with_cluster_node():
    cluster_node = MockNode()
    node = MockNode()

    ClusterManager(cluster_node, ..., ...).add_node(node, "")

    assert cluster_node in node.connected_nodes and node in cluster_node.connected_nodes
