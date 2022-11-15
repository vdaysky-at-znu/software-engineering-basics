import datetime

from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency, MatchDependency
from api.models import Event, Player, Match, MapPick, MapPickProcess, Team, Game, MatchTeam
from api.schemas.match import CreateMatch, PickMap
from api.exceptions import PermissionError, BadRequestError
from api.services.match import select_map, finish_mp

router = APIRouter()


@router.get("/testcreate")
async def test_create():

    # get random event
    event = Event.objects.order_by("?").first()

    # get random team
    team_a = Team.objects.order_by("?").first()
    team_b = Team.objects.order_by("?").first()

    # create match
    match = Match.objects.create(
        event=event,
        team_one=team_a,
        team_two=team_b,
        map_count=1,
        start_date=datetime.datetime.now(),
        name="test match",
        game_meta={
            "mode": Game.Mode.COMPETITIVE,
        }
    )

    return match


@router.post('/create')
async def create_match(data: CreateMatch, player: Player = PlayerAuthDependency):

    if not player.has_perm('api.can_create_matches'):
        raise PermissionError

    match = Match.objects.create(
        name=data.name,
        start_date=data.start_date,
        event=data.event,
        team_one=MatchTeam.from_team(data.team_a),
        team_two=MatchTeam.from_team(data.team_b),
        map_count=data.map_count,
        game_meta={
            "mode": Game.Mode.COMPETITIVE,
        }
    )

    # TODO: somehow determine who picks first
    match.map_pick_process.turn = match.get_random_team()
    # TODO: somehow determine who picks for each team
    match.map_pick_process.picker_a = match.team_one.players.first()
    match.map_pick_process.picker_b = match.team_two.players.first()
    match.map_pick_process.save()

    return match.id


@router.post('/map-pick')
async def pick_map(data: PickMap, player: Player = PlayerAuthDependency):
    await select_map(data.map, player)


@router.get('/{match}/finish-pick')
async def get_map_pick(match: Match = MatchDependency):
    await finish_mp(match)
