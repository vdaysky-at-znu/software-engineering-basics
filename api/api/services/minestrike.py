import logging
from typing import Optional, Dict

from api.consumers import WsPool, WsConn
from api.events.event import EventOut


class MineStrike:
    """
        Wrapper on top of WebsocketConnection to provide a
        simplified interface as a way to communicate with
        remote Bukkit plugin.
    """

    def __init__(self, server_id):
        self.server_id = server_id

        self.event_queue = []

        @WsPool.on_bukkit_connect(self.server_id)
        async def send_queued_events():
            while self.event_queue:
                await self.safe_send_event(self.event_queue.pop(0))

    def get_conn(self) -> WsConn:
        return WsPool.get_bukkit_server(self.server_id)

    async def safe_send_event(self, evt) -> Optional[Dict]:
        if self.get_conn() is None:
            self.event_queue.append(evt)
            logging.warning(f"Event {evt.type} queued, no coroutine returned")
            return

        return await self.get_conn().send_event(evt)

    async def model_update(self, model, pk=None):

        if isinstance(model, str):
            model_name = model
            model_pk = pk
        else:
            string = type(model).__name__
            model_name = string[0].lower() + string[1:]
            model_pk = model.pk

        evt = EventOut(
            type=EventOut.Type.MODEL_UPDATE,
            payload={
                "model_name": model_name,
                "model_pk": model_pk,
            }
        )

        return await self.safe_send_event(evt)

    async def update_server(self):
        """
            Server stores lobbies and hubs, so this method
            can be called to make minestrike update saved lists
        """
        await self.model_update("server", self.server_id)

    async def join_game(self, game, player, team):

        evt = EventOut(
            type="PlayerGameConnectEvent",
            payload={
                "player_id": player.id,
                "game_id": game.id,
                "team_id": team.id,
                "is_spectating": False,
            }
        )

        return await self.safe_send_event(evt)

    async def leave_game(self, game, player):
        evt = EventOut(
            type="PlayerLeaveGameBackendEvent",
            payload={
               "player_id": player.id,
               "game_id": game.id,
            }
        )
        await self.safe_send_event(evt)

    async def update_team(self, in_game_team):
        return await self.model_update(in_game_team)

    async def update_game(self, game):
        return await self.model_update(game)

