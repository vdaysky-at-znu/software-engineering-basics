from api.models import Match, InGameTeam, PlayerSession
from api.services import internalHandler


@internalHandler.on("MapPickDone")
async def on_map_pick_done(match: Match, payload):
    # create games with maps from map pick
    for map_pick in match.map_pick_process.picked.all().order_by("id"):

        game = match.games.create(
            map=map_pick.map_codename,
            team_a=InGameTeam.from_team(match.team_one, is_ct=True),
            team_b=InGameTeam.from_team(match.team_two, is_ct=False),
            plugins=[
                'WarmUpPlugin',
                'DefusalPlugin',
            ]
        )

        # only participants are allowed
        game.whitelist.add(*match.team_one.players.all(), *match.team_two.players.all())
