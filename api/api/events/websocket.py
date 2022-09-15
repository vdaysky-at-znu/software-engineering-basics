from api.consumers import WebsocketConnection, WsSessionManager
from api.events.event import EventOut
from api.events.manager import EventManager
from api.events.schemas.websocket import BukkitInitEvent, PingEvent, ConfirmEvent
from api.exceptions import AuthorizationError

WsEventManager = EventManager()

# TODO: rename events on bukkit side


@WsEventManager.on(ConfirmEvent)
async def confirm(consumer: WebsocketConnection, event: ConfirmEvent):
    future = consumer.awaiting_response[event.confirm_message_id]
    future.set_result(event)
    return


@WsEventManager.on(PingEvent)
async def confirm_ping(consumer: WebsocketConnection, event: PingEvent):
    evt = EventOut(
        type="PING",
        payload={"ping_id": event.ping_id}
    )

    await consumer.send_event(evt)


@WsEventManager.on(BukkitInitEvent)
async def init_bukkit(consumer: WebsocketConnection, event: BukkitInitEvent):

    # todo: secret authentication
    if event.secret is None:
        raise AuthorizationError

    consumer.is_bukkit = True

    WsSessionManager.add_bukkit_server(consumer)

    evt = EventOut(
        type="ACK_CONN",
        message="Acknowledge server connection. Welcome back, Bukkit"
    )

    await consumer.send_event(evt)
