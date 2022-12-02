import logging
import os

import uvicorn
from django.core.wsgi import get_wsgi_application
from fastapi_utils.tasks import repeat_every
from starlette.middleware.base import BaseHTTPMiddleware

from middleware import DBConnectionSanitizerMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms.settings')
application = get_wsgi_application()

from api.routes.routers import get_v1_router
from starlette.requests import HTTPConnection

from fastapi import FastAPI

from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLWSHandler, GraphQLTransportWSHandler

from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

from api.consumers import WsConn

from api.exceptions import install_exception_handlers

from api.graphql.query import schema

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

# Configuring logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# mw = DBConnectionSanitizerMiddleware()
app.add_middleware(DBConnectionSanitizerMiddleware)

app.include_router(prefix="/api", router=get_v1_router())


@app.get("/status")
def status():
    return {
        "success": True
    }


@app.on_event("startup")
@repeat_every(seconds=60, raise_exceptions=True)
async def keep_open_servers():
    """ A task that runs every minute to keep open servers.
        Ideally servers should be created on events,
        but this is a fallback.
    """
    from api.tasks.game import keep_open_pubs, keep_open_deathmatch, keep_open_duels
    await keep_open_pubs()
    await keep_open_deathmatch()
    await keep_open_duels()


# init handlers


class AuthBackend(AuthenticationBackend):

    async def authenticate(self, conn: HTTPConnection):
        from django.contrib.sessions.models import Session
        from django.contrib.auth.models import User, AnonymousUser
        sess_id = conn.headers.get('session_id')
        if sess_id is not None:
            session = Session.objects.filter(session_key=sess_id)
            if session.exists():
                session_data = session.get().get_decoded()
                uid = session_data.get('_auth_user_id')
                if uid is not None:
                    user = User.objects.filter(id=uid)
                    if user.exists():
                        return sess_id, user.get()
        return None, AnonymousUser()


app.add_middleware(
    AuthenticationMiddleware,
    backend=AuthBackend()
)


app.mount("/graphql", GraphQL(schema, debug=True))

install_exception_handlers(app)

from api.signals import register_signals

register_signals()


@app.websocket("/ws/connect")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conn = WsConn(websocket)
    await conn.run()

