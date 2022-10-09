from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency, MatchDependency
from api.models import Event, Player, Match, MapPick, MapPickProcess
from api.schemas.match import CreateMatch, PickMap
from api.exceptions import PermissionError, BadRequestError
from api.services.match import select_map, finish_mp

router = APIRouter()


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
