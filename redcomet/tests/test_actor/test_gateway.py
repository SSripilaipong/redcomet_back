from redcomet.base.actor import ActorRefAbstract
from redcomet.base.actor.abstract import ActorAbstract
from redcomet.base.actor.message import MessageAbstract
from redcomet.base.cluster.ref import ClusterRefAbstract
from redcomet.system import ActorSystem


class Ping(MessageAbstract):
    pass


class Pong(MessageAbstract):
    pass


class MyActor(ActorAbstract):
    def receive(self, message: MessageAbstract, sender: ActorRefAbstract, me: ActorRefAbstract,
                cluster: ClusterRefAbstract):
        if isinstance(message, Ping):
            sender.tell(Pong())
        else:
            raise NotImplementedError()


def test_should_reply_to_gateway():
    with ActorSystem.create() as system:
        actor = system.spawn(MyActor())
        actor.tell(Ping())
        reply = system.fetch_message(timeout=1)
        assert isinstance(reply, Pong)
