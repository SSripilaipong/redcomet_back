from multiprocessing import Queue

from redcomet.base.messaging.handler import PacketHandlerAbstract
from redcomet.messenger import Messenger
from redcomet.messenger.address_cache import AddressCache
from redcomet.messenger.inbox.process_safe import ProcessSafeInbox
from redcomet.messenger.inbox.synchronous import SynchronousInbox
from redcomet.messenger.outbox import Outbox


def create_messenger(handler: PacketHandlerAbstract, address_cache: AddressCache = None, *,
                     actor_id: str = "messenger", parallel: bool = False) -> Messenger:
    if not parallel:
        inbox = SynchronousInbox(handler)
    else:
        inbox = ProcessSafeInbox(Queue(), handler)

    return Messenger(actor_id, inbox, Outbox(), address_cache=address_cache)