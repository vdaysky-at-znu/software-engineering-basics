import asyncio
from datetime import datetime

from api.events.event import AbsEvent
from api.models import Player, PlayerQueue, Match, MapPickProcess, Game, PlayerSession, MatchTeam
from api.events.internal import internalHandler


async def join_queue(player: Player, queue: PlayerQueue):
    if queue.locked:
        return {
            'success': False,
            'message': 'Queue is locked'
        }

    if not queue.join(player):
        return {
            'success': False,
            'message': 'Player already in queue'
        }

    await internalHandler.propagate_abstract_event(AbsEvent(name='PlayerJoinQueue', payload={'player': player}), queue)

    return {
        'success': True,
        'message': 'Player joined queue'
    }


async def leave_queue(player: Player, queue: PlayerQueue):
    if queue.locked:
        return {
            'success': False,
            'message': 'Queue is locked'
        }

    if not queue.leave(player):
        return {
            'success': False,
            'message': 'Player not in queue'
        }

    await internalHandler.propagate_abstract_event(AbsEvent(name='PlayerLeaveQueue', payload={'player': player}), queue)

    return {
        'success': True,
    }


async def confirm_queue(player: Player, queue: PlayerQueue):
    # can only confirm game once queue is locked
    if not queue.locked:
        return {
            'success': False,
            'message': 'Queue is not locked'
        }

    if not queue.confirm(player):
        return {
            'success': False,
            'message': 'Player already confirmed'
        }

    await internalHandler.propagate_abstract_event(AbsEvent(name='PlayerConfirmQueue', payload={'player': player}), queue)

    return {
        'success': True,
        'message': 'Player confirmed queue'
    }


async def pick_player(captain: Player, player: Player, queue: PlayerQueue):

    # player is not a captain
    if not queue.captain_a == captain and not queue.captain_b == captain:
        return {
            'success': False,
            'message': 'Player is not a captain'
        }

    captain_is_a = queue.captain_a == captain

    match = queue.match

    a_players = match.team_one.players.count()
    b_players = match.team_two.players.count()

    # not your turn
    if captain_is_a and a_players != b_players:
        return {
            'success': False,
            'message': 'Not your turn'
        }

    if not captain_is_a and a_players - b_players != 1:
        return {
            'success': False,
            'message': 'Not your turn'
        }

    # queue wasn't confirmed yet (how did we get captains then?)
    if not queue.confirmed:
        return {
            'success': False,
            'message': 'Queue not confirmed'
        }

    # player already picked
    if match.team_one.players.filter(id=player.id).exists() or match.team_two.players.filter(id=player.id).exists():
        return {
            'success': False,
            'message': 'Player already picked'
        }

    # add player to captain's match team
    match.team_one.players.add(player) if queue.captain_a == captain else match.team_two.players.add(player)

    await internalHandler.propagate_abstract_event(AbsEvent(name='PlayerPicked', payload={'player': player}), queue)

    return {
        'success': True,
        'message': 'Player picked'
    }


@internalHandler.on("PlayerConfirmQueue")
async def on_queue_confirmation(queue: PlayerQueue, payload):
    # check if all players accepted
    if queue.confirmed_players.count() == 10:
        queue.confirmed = True
        queue.save()
        await internalHandler.propagate_abstract_event(AbsEvent(name='QueueConfirmed', payload={}), queue)
        return


@internalHandler.on("PlayerJoinQueue")
async def on_player_join_queue(queue: PlayerQueue, payload):

    # check if queue is full
    if queue.players.count() != 10:
        return

    # lock queue
    queue.lock()

    # queue is locked, meaning match confirmation started
    # make sure that in 30 seconds QueueConfirmed event will be fired
    try:
        await internalHandler.wait("QueueConfirmed", timeout=30).on(queue)
    except TimeoutError:
        # Timed out: did not receive enough confirmations

        # get players who didn't accept
        confirmed_ids = queue.confirmed_players.values_list('id', flat=True)
        not_confirmed = queue.players.exclude(id__in=confirmed_ids)

        # remove players who didn't accept from queue
        queue.players.remove(*not_confirmed)

        # unlock queue, let new players in
        queue.unlock()

        # delete all player confirmations
        queue.unconfirm()


@internalHandler.on("QueueConfirmed")
async def on_queue_confirmed(queue: PlayerQueue, payload):
    # select two captains with highest elo
    captain_a, captain_b = queue.players.all().order_by('-elo')[:2]

    # create match
    match = Match.objects.create(
        team_one=MatchTeam.objects.create(name=f"Team_{captain_a.username}"),
        team_two=MatchTeam.objects.create(name=f"Team_{captain_b.username}"),
        name=f'Team_{captain_a.username} vs Team_{captain_b.username}',
        start_date=datetime.now(),
        map_count=1,
        game_meta={
            'mode': Game.Mode.RANKED,
        }
    )
    # Captains belong to their team instantly
    match.team_one.players.add(captain_a)
    match.team_two.players.add(captain_b)

    # by default captain_a is picking first
    match.map_pick_process.turn = captain_a
    match.map_pick_process.picker_a = captain_a
    match.map_pick_process.picker_b = captain_b
    match.map_pick_process.save()

    queue.match = match
    queue.captain_a = captain_a
    queue.captain_b = captain_b

    queue.save()

    # wait for map pick to finish
    await internalHandler.wait("MapPickDone").post(match)

    # manage players inside game
    # note: in-game teams are not filled here.
    for game in match.games.all():

        # register whitelist
        game.whitelist.add(*queue.players.all())
