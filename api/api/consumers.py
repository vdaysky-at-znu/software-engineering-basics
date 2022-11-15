from __future__ import annotations

import asyncio
import logging
from asyncio import Future
from collections import defaultdict
from typing import Dict, Optional, List

from django.db.models import Model
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from api.events.event import EventOut, AbsEvent
from api.models import Player, AuthSession


class Subscription:

    def __init__(self, model: str, model_id: dict):
        self.model = model
        self.model_id = id


class WsPool:
    """ Stores every websocket consumer instance associated with session. """

    # associate user ID with websocket connection wrapper
    _session_registry: Dict[int, WsConn] = {}

    # store all connections
    _connections: List[WsConn] = []

    # store bukkit connection separately
    _bukkit: Optional[WsConn] = None

    # tasks to do when bukkit server comes online
    _on_connect_handlers = defaultdict(list)

    @classmethod
    def set_bukkit(cls, conn):
        cls._bukkit = conn

        # run handlers
        for server_id, handlers in cls._on_connect_handlers.items():
            for handler in handlers:
                asyncio.create_task(handler())

    @classmethod
    def get_bukkit_server(cls, server_id=None) -> WsConn:
        return cls._bukkit

    @classmethod
    def authorize_connection(cls, session, conn):
        cls._session_registry[session.id] = conn

    @classmethod
    def register_connection(cls, conn):
        cls._connections.append(conn)

    @classmethod
    def disconnect(cls, conn: WsConn):
        """ Once websocket disconnected, we forget it ever existed """
        if cls._bukkit == conn:
            cls._bukkit = None

        for k, v in cls._session_registry.items():
            if v == conn:
                break
        else:
            return

        cls._connections.remove(conn)
        del cls._session_registry[k]

    @classmethod
    async def model_event(cls, event: str, instance: Model):
        """ Send events to listeners on frontend """

        evt = None

        if event == "update":
            evt = EventOut(type=EventOut.Type.MODEL_UPDATE, payload={
                "model_name": type(instance).__name__.lower(),
                "model_pk": instance.id,
            })

        if event == "create":
            evt = EventOut(type=EventOut.Type.MODEL_CREATE, payload={
                "model_name": type(instance).__name__.lower(),
                "model_pk": instance.id,
            })

        if not event:
            return

        WsPool.broadcast_event(evt)

    @classmethod
    def broadcast_event(cls, evt: EventOut):

        print(f"broadcast to {len(cls._connections)}")
        for conn in cls._connections:

            # remove disconnected clients
            if conn.websocket.client_state == 3:
                cls._connections.remove(conn)
                continue

            asyncio.create_task(conn.send_event(evt))

        if cls._bukkit:
            asyncio.create_task(cls._bukkit.send_event(evt))

    @classmethod
    def on_bukkit_connect(cls, server_id):
        def inner(func):
            cls._on_connect_handlers[server_id].append(func)
            return func
        return inner

    @classmethod
    def get_conn(cls, session_id) -> Optional[WsConn]:
        return cls._session_registry.get(session_id)

    @classmethod
    def get_player_conn(cls, player: Player) -> Optional[WsConn]:
        for sess_id, conn in cls._session_registry.items():
            if AuthSession.objects.get(id=sess_id).player == player:
                return conn


class WsConn:
    """ FastAPI websocket connection wrapper """

    def __init__(self, websocket: WebSocket):

        self.websocket = websocket
        self.session = None
        self.is_bukkit = False
        self.awaiting_response = {}
        self.subscriptions: List[Subscription] = []

        # register connection, no matter if it's authorized or not
        WsPool.register_connection(self)

    def subscribe(self, sub: Subscription):
        self.subscriptions.append(sub)

    async def run(self):
        """ Keep reading and dispatching events """

        from api.events.websocket import WsEventManager

        while True:
            try:
                data = await self.websocket.receive_json()
            except WebSocketDisconnect:
                return WsPool.disconnect(self)

            try:
                # parse event with name and payload
                event = AbsEvent.parse_obj(data)
            except ValidationError:
                logging.error(f"Malformed event received: {data}")
                continue

            # handle without blocking.
            # We will be waiting for confirmation message from client
            # so blocking is a stupid idea
            coro = WsEventManager.propagate_abstract_event(event, self)
            asyncio.create_task(coro)

    async def send_event(self, event: EventOut) -> Optional[Dict]:

        if self.websocket.client_state == WebSocketState.DISCONNECTED:
            WsPool.disconnect(self)
            return

        response = Future()
        self.awaiting_response[event.message_id] = response

        await self.websocket.send_json(event.dict())
        return await response
