from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency, MatchDependency
from api.models import Event, Player, Match
from api.schemas.match import CreateMatch, PickMap
from api.exceptions import PermissionError, BadRequestError
router = APIRouter()


@router.post('/create')
def create_match(data: CreateMatch, player: Player = PlayerAuthDependency):

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

    return match


@router.post('/{match}/map-pick')
def pick_map(data: PickMap, match: Match = MatchDependency, player: Player = PlayerAuthDependency):

    # Parse request
    map = data.map
    is_picked = data.is_picked

    # Determine constant
    NULL = 0
    BAN = 1
    PICK = 2
    DEFAULT = 3
    action_name = PICK if is_picked else BAN

    # Find out who tries to vote
    team = player.team

    # look up pick process
    map_pick_process = match.map_pick_process

    if map_pick_process.turn is None:
        map_pick_process.turn = match.get_random_team()
        map_pick_process.save()

    # count some stats prior to picking
    maps_banned = map_pick_process.banned.count()
    maps_picked = map_pick_process.picked.count()
    map_count = match.map_count
    selected_maps = maps_banned + maps_picked

    if map_pick_process.finished:
        raise BadRequestError

    if map_pick_process.turn != team:

        if match.other_team(map_pick_process.turn) != team:
            raise BadRequestError

        raise BadRequestError("Wait for your turn")

    if map_pick_process.next_action != action_name:
        raise BadRequestError

    map_object = map_pick_process.maps.fitler(map_name=map)

    if map_object.was_selected():
        raise BadRequestError('Map was already selected')

    # mark map as selected
    map_object.picked = is_picked
    map_object.selected_by = team
    map_object.save()

    # update count after last action
    maps_banned += not is_picked
    maps_picked += is_picked

    # Now that validation is done we have to determine next action
    next_action = None

    # first two are always ban
    if maps_banned < 2:
        next_action = BAN

    # after initial bans we pick one less than actual map count
    elif maps_picked < map_count - 1:
        next_action = PICK

    # after that we ban until decider is found
    elif 7 - 1 > selected_maps >= 2 + map_count - 1:
        next_action = BAN

    # Last is always picked by default
    elif selected_maps == 6:
        next_action = NULL

        map_left = map_pick_process.maps.get(selected_by=None)
        map_left.picked = True
        map_left.selected_by = None
        map_left.save()

    # save next action
    map_pick_process.next_action = next_action
    map_pick_process.save()

    return
