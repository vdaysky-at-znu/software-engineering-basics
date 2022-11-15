from django.db import connections


class DBConnectionSanitizerMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        await self.app(scope, receive, send)
        for conn in connections.all():
            conn.close()
