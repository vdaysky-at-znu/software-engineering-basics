import datetime

from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency, MatchDependency
from api.models import Event, Player, Match, MapPick, MapPickProcess, Team
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
        team_one=data.team_a,
        team_two=data.team_b,
        map_count=data.map_count
    )

    # TODO: somehow determine who picks first
    match.map_pick_process.turn = match.get_random_team()
    match.map_pick_process.save()

    return match.id


@router.post('/map-pick')
async def pick_map(data: PickMap, player: Player = PlayerAuthDependency):
    await select_map(data.map, player)


@router.get('/{match}/finish-pick')
async def get_map_pick(match: Match = MatchDependency):
    await finish_mp(match)
