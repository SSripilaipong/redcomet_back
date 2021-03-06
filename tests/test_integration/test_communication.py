import time

import pytest

from redcomet.actor.ref import ActorRef
from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.base.messaging.address import Address
from redcomet.messenger.inbox.queue import QueueAbstract
from redcomet.implementation.messenger.inbox.queue.process_safe import ProcessSafeQueueManager
from redcomet.system import ActorSystem


class MyStringMessage(MessageAbstract):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f"MyStringMessage({self.value!r})"


class IntroduceMessage(MessageAbstract):
    def __init__(self, address: Address):
        self.address = address

    def __repr__(self) -> str:
        return f"IntroduceMessage({self.address!r})"


class First(ActorAbstract):

    def __init__(self, recv_queue: QueueAbstract):
        self._recv_queue = recv_queue
        self._second = None

    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        if isinstance(message, IntroduceMessage):
            self._second = message.address
        elif isinstance(message, MyStringMessage):
            if message.value == "hi to second":
                ActorRef(..., ..., self._second).bind(me).tell(MyStringMessage("HI FROM FIRST"))
            else:
                self._recv_queue.put(message.value)
        else:
            raise NotImplementedError()

    def __repr__(self) -> str:
        return "<First>"


class Second(ActorAbstract):
    def __init__(self, first: Address, recv_queue: QueueAbstract):
        self._first = first
        self._recv_queue = recv_queue

    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        if isinstance(message, MyStringMessage):
            if message.value == "hi to first":
                ActorRef(..., ..., self._first).bind(me).tell(MyStringMessage("HI FROM SECOND"))
            else:
                self._recv_queue.put(message.value)
        else:
            raise NotImplementedError()

    def __repr__(self) -> str:
        return "<Second>"


@pytest.mark.integration
def test_should_communicate_between_actors():
    with ProcessSafeQueueManager() as first_queue, ProcessSafeQueueManager() as second_queue:
        with ActorSystem.create(parallel=True) as system:
            first = system.spawn(First(first_queue))
            second = system.spawn(Second(first.address, second_queue))

            time.sleep(0.1)
            first.tell(IntroduceMessage(second.address))

            first.tell(MyStringMessage("hi to second"))
            message_second = second_queue.get(timeout=2)
            assert message_second == "HI FROM FIRST"

            time.sleep(0.01)
            second.tell(MyStringMessage("hi to first"))
            message_first = first_queue.get(timeout=2)
            assert message_first == "HI FROM SECOND"
