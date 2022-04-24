from typing import Dict

from redcomet.actor.ref import ActorRef
from redcomet.base.actor import ActorAbstract
from redcomet.base.cluster.abstract import ClusterAbstract
from redcomet.base.executor import ExecutorAbstract
from redcomet.base.message.abstract import MessageAbstract
from redcomet.base.node import NodeAbstract
from redcomet.cluster import Cluster


class Executor(ExecutorAbstract):
    def __init__(self, node_id: str, node: NodeAbstract = None, cluster: Cluster = None):
        self._node_id = node_id
        self._node = node
        self._cluster = cluster
        self._actor_map: Dict[str, ActorAbstract] = {}

    def set_node(self, node: NodeAbstract):
        self._node = node

    def set_cluster(self, cluster: ClusterAbstract):
        self._cluster = cluster

    def register(self, local_id: str, actor: ActorAbstract):
        if local_id in self._actor_map:
            raise NotImplementedError()

        self._actor_map[local_id] = actor

    def execute(self, message: MessageAbstract, sender: ActorRef, local_actor_id: str):
        actor = self._actor_map.get(local_actor_id)
        if actor is None:
            raise NotImplementedError()

        me = ActorRef.create(self._node, local_actor_id, self._node.make_global_id(local_actor_id))
        self._cluster.set_running_actor_local_id(local_actor_id)
        try:
            actor.receive(message, sender, me, self._cluster)
        except Exception:
            raise NotImplementedError()