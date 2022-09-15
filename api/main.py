import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms.settings')
application = get_wsgi_application()

from api.routes.routers import get_v1_router
from starlette.requests import HTTPConnection

from fastapi import FastAPI

from ariadne.asgi import GraphQL

from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

from api.consumers import WebsocketConnection

from api.exceptions import install_exception_handlers

from api.graphql.query import schema

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prefix="/api", router=get_v1_router())


@app.get("/status")
def status():
    return {
        "success": True
    }


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
    print("new websocket connection")
    conn = WebsocketConnection(websocket)
    await conn.run()
