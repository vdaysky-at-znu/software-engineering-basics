from __future__ import annotations

import asyncio
from asyncio import Future
from collections import defaultdict
from typing import Dict, Optional, List

from django.db.models import Model
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from api.events.event import EventOut, AbsEvent


class WsSessionManager:
    """ Stores every websocket consumer instance associated with session. """

    # user.id: consumer
    _session_registry: Dict[int, WebsocketConnection] = {}
    _connections: List[WebsocketConnection] = []
    _bukkit: Optional[WebsocketConnection] = None

    _on_connect_handlers = defaultdict(list)

    @classmethod
    def add_bukkit_server(cls, conn):
        cls._bukkit = conn

        for server_id, l in cls._on_connect_handlers.items():
            for h in l:
                asyncio.create_task(h())

    @classmethod
    def get_bukkit_server(cls, server_id=None) -> WebsocketConnection:
        return cls._bukkit

    @classmethod
    def authorize_connection(cls, session, conn):
        cls._session_registry[session.id] = conn

    @classmethod
    def register_connection(cls, conn):
        cls._connections.append(conn)

    @classmethod
    def disconnect(cls, conn):
        """ Once websocket disconnected, we forget it ever existed """
        if cls._bukkit == conn:
            cls._bukkit = None

        for k, v in cls._session_registry.items():
            if v == conn:
                break
        else:
            return

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

        WsSessionManager.broadcast_event(evt)

    @classmethod
    def broadcast_event(cls, evt: EventOut):

        print(f"broadcast to {cls._connections}")
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
    def get_conn(cls, session_id):
        return cls._session_registry.get(session_id)


class WebsocketConnection:
    """ FastAPI websocket connection """

    def __init__(self, websocket: WebSocket):

        self.websocket = websocket
        self.session = None
        self.is_bukkit = False
        self.awaiting_response = {}

        # register connection, no matter if it's authorized or not
        WsSessionManager.register_connection(self)

    async def run(self):
        """ Keep reading and dispatching events """

        from api.events.websocket import WsEventManager

        while True:
            try:
                data = await self.websocket.receive_json()
            except WebSocketDisconnect:
                return WsSessionManager.disconnect(self.session)

            # parse event with name and payload
            event = AbsEvent.parse_obj(data)

            # handle without blocking.
            # We will be waiting for confirmation message from client
            # so blocking is a stupid idea
            coro = WsEventManager.propagate_event(event, self)
            asyncio.create_task(coro)

    async def send_event(self, event: EventOut):

        if self.websocket.client_state == WebSocketState.DISCONNECTED:
            WsSessionManager.disconnect(self)
            raise ValueError("Client disconnected")

        response = Future()
        self.awaiting_response[event.message_id] = response

        await self.websocket.send_json(event.dict())
        return await response
