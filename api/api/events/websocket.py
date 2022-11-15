import logging
import traceback

from api.consumers import WsConn, WsPool
from api.events.event import EventOut
from api.events.manager import EventManager
from api.events.schemas.websocket import BukkitInitEvent, PingEvent, ConfirmEvent
from api.exceptions import AuthorizationError

WsEventManager = EventManager()


@WsEventManager.on(ConfirmEvent)
async def confirm(consumer: WsConn, event: ConfirmEvent):
    # TODO: response payload?
    msg_id = event.confirm_message_id

    if msg_id not in consumer.awaiting_response:
        logging.warning("")
        return

    future = consumer.awaiting_response[msg_id]
    logging.info(f"Confirming message {msg_id} ({future})")
    try:
        future.set_result(event.payload)
        consumer.awaiting_response.pop(msg_id)
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Error while setting future result: {e}")
    return


@WsEventManager.on(PingEvent)
async def confirm_ping(consumer: WsConn, event: PingEvent):
    evt = EventOut(
        type="PING",
        payload={"ping_id": event.ping_id}
    )

    await consumer.send_event(evt)


@WsEventManager.on(BukkitInitEvent)
async def init_bukkit(consumer: WsConn, event: BukkitInitEvent):

    # todo: secret authentication
    if event.secret is None:
        raise AuthorizationError

    consumer.is_bukkit = True

    WsPool.set_bukkit(consumer)

    evt = EventOut(
        type="ACK_CONN",
        message="Acknowledge server connection. Welcome back, Bukkit"
    )

    await consumer.send_event(evt)
