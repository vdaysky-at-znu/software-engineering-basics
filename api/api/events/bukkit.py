import logging

from api.events.event import IntentResponse
from api.events.schemas.bukkit import ServerStartEvent, CreateGameIntentEvent, PlayerJoinGameIntentEvent, \
    PlayerLeaveGameEvent, PlayerTeamChangeIntentEvent, PreGameEndEvent, GameStartedEvent, PlayerJoinServerEvent, \
    PlayerLeaveServerEvent, PlayerDeathEvent
from api.schemas.permission import Permission
from api.services.game import join_game, find_team_for_player, PLUGIN_MAP, create_game
from api.services.minestrike import MineStrike
from api.events.manager import EventManager
from api.models import InGameTeam, Game, Player, PlayerSession, Map, GamePlayerEvent, Round
from api.services.permission import has_permission
from api.services.ranked import compute_elo

BukkitEventManager = EventManager()


@BukkitEventManager.on(ServerStartEvent)
async def on_plugin_start(minestrike: MineStrike, event: ServerStartEvent):
    print("server started")


@BukkitEventManager.on(CreateGameIntentEvent)
async def on_game_create_request(minestrike: MineStrike, event: CreateGameIntentEvent):

    if not has_permission(event.player, Permission.Game.Create):
        return IntentResponse.failure(
            "You don't have permission to create games"
        )

    mode = Game.Mode.to_code(event.mode)

    if mode is None:
        return IntentResponse.failure(
            f"Unknown game mode {event.mode}"
        )

    map = Map.objects.filter(name=event.mapName).first()

    if not map:
        return IntentResponse.failure(
            f"Unknown map {event.mapName}"
        )

    game = await create_game(
        map=map,
        mode=mode,
    )

    # update server object effectively updating list of games
    await minestrike.update_server()

    return IntentResponse.success(
        f"Game created, it's ID is {game.id}",
        game_id=game.id,
    )


@BukkitEventManager.on(PlayerJoinGameIntentEvent)
async def on_player_request_join_game(minestrike: MineStrike, event: PlayerJoinGameIntentEvent):

    game: Game = event.game
    player: Player = event.player

    # TODO: optionally save player join game event?

    roster = find_team_for_player(game, player)

    if not player.can_join_game(
            game=game,
            roster=roster,
            status=PlayerSession.Status.PARTICIPATING
    ):
        return IntentResponse.failure(
            f"Cannot join game {game.id}"
        )

    await join_game(
        game=game,
        player=player,
        status=PlayerSession.Status.PARTICIPATING,
        roster=roster
    )

    return IntentResponse.success(
        "You have been added to the game"
    )


@BukkitEventManager.on(PlayerLeaveGameEvent)
async def on_player_leave_game(minestrike: MineStrike, event: PlayerLeaveGameEvent):

    game = event.game
    player = event.player

    session: PlayerSession = game.get_session(player)

    # mark session as away
    session.state = PlayerSession.State.AWAY
    session.save()


@BukkitEventManager.on(PlayerTeamChangeIntentEvent)
async def on_player_request_team_change(minestrike: MineStrike, event: PlayerTeamChangeIntentEvent):

    game = event.game
    player = event.player

    roster = game.get_team(event.team)

    session = game.get_session(player)
    session.roster = roster

    # todo: just an idea, i could modify save method to return a coroutine
    #  that is resolved when bukkit confirms handling
    session.save()


@BukkitEventManager.on(PreGameEndEvent)
async def on_game_end(minestrike: MineStrike, event: PreGameEndEvent):

    game = event.game

    if None not in (event.looser, event.winner):
        winner = event.looser
        looser = event.winner

        game.winner = winner

        if game.has_plugin("RankedPlugin"):
            win, loose = compute_elo(winner, looser)

            winner.award_elo(win)

            win, loose = compute_elo(looser, winner)

            looser.deduct_elo(loose)

    game.finished = True
    game.save()


@BukkitEventManager.on(GameStartedEvent)
async def on_game_start(minestrike: MineStrike, event: GameStartedEvent):
    game = event.game
    game.started = True
    game.save()


@BukkitEventManager.on(PlayerJoinServerEvent)
async def on_player_join_server(minestrike: MineStrike, event: PlayerJoinServerEvent):
    player = event.player
    player.in_server = True
    player.save()


@BukkitEventManager.on(PlayerLeaveServerEvent)
async def on_player_leave_server(minestrike: MineStrike, event: PlayerLeaveServerEvent):
    player: Player = event.player
    player.in_server = False
    player.save()

    session = player.get_active_session()

    # if player was in game, leave it
    if session:
        session.state = PlayerSession.State.AWAY
        session.save()


@BukkitEventManager.on(PlayerDeathEvent)
async def on_player_death(minestrike: MineStrike, event: PlayerDeathEvent):

    if event.round == -1:
        print("Warmup", event)
        return

    round, created = Round.objects.get_or_create(
        game=event.game,
        number=event.round,
        defaults={
            "game": event.game,
            "number": event.round,
        }
    )

    GamePlayerEvent.objects.create(
        game=event.game,
        player=event.damagee,
        event=GamePlayerEvent.Type.DEATH,
        round=round,
        is_ct=event.game.get_player_team(event.damagee).is_ct,
        meta={
            "damage_source": event.damageSource,  # weapon name / grenade name
            "damage_type": event.reason,  # fire, grenade, gun, etc
            "modifiers": event.modifiers,  # headshot, blinded, wallbangPenalty, etc
        }
    )

    if event.damager:
        GamePlayerEvent.objects.create(
            game=event.game,
            player=event.damager,
            event=GamePlayerEvent.Type.KILL,
            round=round,
            is_ct=event.game.get_player_team(event.damager).is_ct,
            meta={
                "damage_source": event.damageSource,  # weapon name / grenade name
                "damage_type": event.reason,  # fire, grenade, gun, etc
                "modifiers": event.modifiers,  # headshot, blinded, wallbangPenalty, etc
            }
        )

    print(event)
