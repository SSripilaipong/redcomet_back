import pytest

from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.queue.abstract import QueueAbstract
from redcomet.queue.default import DefaultQueue
from redcomet.system import ActorSystem


class MyStringMessage(MessageAbstract):
    def __init__(self, value: str):
        self.value = value


class MyActor(ActorAbstract):
    def __init__(self, recv_queue: QueueAbstract):
        self._recv_queue = recv_queue

    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        self._recv_queue.put(message)


@pytest.mark.integration
def test_should_tell_message():
    queue = DefaultQueue()
    with ActorSystem.create() as system:
        ref = system.spawn(MyActor(queue))
        ref.tell(MyStringMessage("Hello"))

        recv_message = queue.get(timeout=2)

    assert recv_message.value == "Hello"