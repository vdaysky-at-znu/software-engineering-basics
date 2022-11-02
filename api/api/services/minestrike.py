from api.consumers import WsSessionManager
from api.events.event import EventOut


class MineStrike:

    def __init__(self, server_id):
        self.server_id = server_id

        self.event_queue = []

        @WsSessionManager.on_bukkit_connect(self.server_id)
        async def send_queued_events():
            while self.event_queue:
                await self.safe_send_event(self.event_queue.pop(0))

    def get_conn(self):
        return WsSessionManager.get_bukkit_server(self.server_id)

    async def safe_send_event(self, evt):
        if self.get_conn() is None:
            self.event_queue.append(evt)
            return

        await self.get_conn().send_event(evt)

    async def model_upedate(self, model, pk=None):

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

        await self.safe_send_event(evt)

    async def update_server(self):
        """ Server stores lobbies and hubs, so this method
        can be called to make minestrike update saved lists"""
        await self.model_update("server", self.server_id)

    async def join_game(self, game, player, team):

        evt = EventOut(
            type="PlayerJoinGameGrantedEvent",
            payload={
                "player_id": player.id,
                "game_id": game.id,
                "team_id": team.id,
                "is_spectating": False,
            }
        )

        await self.safe_send_event(evt)

    async def leave_game(self, game, player):
        return await self.model_update(game)

    async def update_team(self, in_game_team):
        return await self.model_update(in_game_team)

    async def update_game(self, game):
        return await self.model_update(game)

