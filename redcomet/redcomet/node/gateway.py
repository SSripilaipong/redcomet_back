from redcomet.base.actor import ActorAbstract, ActorRefAbstract
from redcomet.base.executor import ExecutorAbstract
from redcomet.base.inbox import InboxAbstract
from redcomet.base.message.abstract import MessageAbstract
from redcomet.base.node import NodeAbstract
from redcomet.base.outbox import OutboxAbstract
from redcomet.inbox import Inbox
from redcomet.outbox import Outbox
from redcomet.queue.abstract import QueueAbstract


class GatewayNode(NodeAbstract):
    def __init__(self, node_id: str, executor: ExecutorAbstract, outbox: OutboxAbstract, inbox: InboxAbstract,
                 incoming_queue: QueueAbstract):
        self._node_id = node_id
        self._executor = executor
        self._outbox = outbox
        self._inbox = inbox
        self._incoming_queue = incoming_queue

    @classmethod
    def create(cls, node_id: str, outbox: Outbox, inbox: Inbox, incoming_queue: QueueAbstract) -> 'GatewayNode':
        executor = EnqueueExecutor(incoming_queue)
        node = cls(node_id, executor, outbox, inbox, incoming_queue)
        inbox.set_node(node)
        inbox.set_executor(executor)
        return node

    def send(self, message: MessageAbstract, local_id: str, receiver_id: str):
        self._outbox.send(message, local_id, receiver_id)

    def make_global_id(self, local_id: str) -> str:
        return f"{self._node_id}.{local_id}"

    @property
    def node_id(self) -> str:
        return self._node_id

    def register(self, actor: ActorAbstract) -> str:
        raise NotImplementedError()


class EnqueueExecutor(ExecutorAbstract):
    def __init__(self, queue: QueueAbstract):
        self._queue = queue

    def register(self, local_id: str, actor: ActorAbstract):
        pass

    def execute(self, message: MessageAbstract, sender: ActorRefAbstract, local_actor_id: str):
        self._queue.put(message)
