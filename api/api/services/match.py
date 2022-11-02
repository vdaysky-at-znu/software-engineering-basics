from api.events.event import AbsEvent
from api.exceptions import BadRequestError
from api.models import MapPick, Player, MapPickProcess
from api.services import internalHandler


async def select_map(map: MapPick, player: Player):
    process = map.process
    match = process.match
    is_picked = process.next_action == MapPickProcess.Action.PICK

    # Find out who tries to vote
    team = player.team

    # look up pick process
    map_pick_process = match.map_pick_process

    if map_pick_process.turn is None:
        raise BadRequestError("You are not allowed to pick yet")

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

    if map.was_selected():
        raise BadRequestError('Map was already selected')

    # mark map as selected
    map.picked = is_picked
    map.selected_by = team
    map.save()

    # update count after last action
    maps_banned += not is_picked
    maps_picked += is_picked

    selected_maps += 1

    # Now that validation is done we have to determine next action
    next_action = None

    # first two are always ban
    if maps_banned < 2:
        next_action = MapPickProcess.Action.BAN

    # after initial bans we pick one less than actual map count
    elif maps_picked < map_count - 1:
        next_action = MapPickProcess.Action.PICK

    # Last is always picked by default
    elif selected_maps == 6:
        next_action = MapPickProcess.Action.NULL

        map_pick_process.finished = True

        map_left = map_pick_process.maps.get(selected_by=None)
        map_left.picked = True
        map_left.selected_by = None
        map_left.save()

    # after that we ban until decider is found
    else:
        next_action = MapPickProcess.Action.BAN

    # save next action
    map_pick_process.next_action = next_action

    if not map_pick_process.finished:
        map_pick_process.turn = match.other_team(map_pick_process.turn)
    else:
        map_pick_process.turn = None

    map_pick_process.save()

    print(f"Is map pick process finished? {map_pick_process.finished}")
    if map_pick_process.finished:
        await internalHandler.propagate_event(AbsEvent(name='MapPickDone', payload={}), match)


async def finish_mp(match):
    await internalHandler.propagate_event(AbsEvent(name='MapPickDone', payload={}), match)
