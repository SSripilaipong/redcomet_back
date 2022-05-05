from redcomet.implementation.messenger.inbox.queue.process_safe import ProcessSafeQueueManager
from redcomet.messaging.handler import PacketHandler
from redcomet.messenger import Messenger
from redcomet.messenger.address_cache import AddressCache
from redcomet.messenger.inbox.process_safe import ProcessSafeInbox
from redcomet.messenger.inbox.queue import QueueAbstract, QueueManagerAbstract
from redcomet.messenger.inbox.synchronous import SynchronousInbox
from redcomet.messenger.outbox import Outbox
from redcomet.node.executor import ActorExecutorAbstract


def create_messenger(handler: ActorExecutorAbstract, address_cache: AddressCache = None, *,
                     actor_id: str = "messenger", inbox_queue_manager: QueueManagerAbstract = None,
                     inbox_queue: QueueAbstract = None, parallel: bool = False) -> Messenger:
    handler = PacketHandler(handler)
    if not parallel:
        inbox = SynchronousInbox(handler)
    else:
        inbox_queue_manager = inbox_queue_manager or ProcessSafeQueueManager()
        inbox_queue = inbox_queue or inbox_queue_manager.start()
        inbox = ProcessSafeInbox(inbox_queue_manager, inbox_queue, handler)

    return Messenger(actor_id, inbox, Outbox(), address_cache=address_cache)
