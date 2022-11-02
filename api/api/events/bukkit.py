from api.events.schemas.bukkit import ServerStartEvent, RequestCreateGameEvent, RequestPlayerJoinGameEvent, \
    PlayerLeaveGameEvent, RequestPlayerTeamChangeEvent, PreGameEndEvent, GameStartedEvent
from api.services.minestrike import MineStrike
from api.events.manager import EventManager
from api.models import InGameTeam, Game, Player, PlayerSession
from api.services.ranked import compute_elo

BukkitEventManager = EventManager()


@BukkitEventManager.on(ServerStartEvent)
async def on_plugin_start(minestrike: MineStrike, event: ServerStartEvent):
    print("server started")


@BukkitEventManager.on(RequestCreateGameEvent)
async def on_game_create_request(minestrike: MineStrike, event: RequestCreateGameEvent):

    team_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)
    team_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)
    plugins = event.plugins

    game = Game.objects.create(
        map=event.mapName,
        match=None,
        team_a=team_a,
        team_b=team_b,
        plugins=plugins,
    )

    # update server object effectively updating list of games
    await minestrike.update_server()

    return game.id


@BukkitEventManager.on(RequestPlayerJoinGameEvent)
async def on_player_request_join_game(minestrike: MineStrike, event: RequestPlayerJoinGameEvent):

    game = event.game
    player = event.player

    session = PlayerSession.objects.filter(game, player).first()

    # TODO: validate that player can join, that's the point of this "backend" shit

    # TODO: optionally save player join game event?

    if session is None:

        session = PlayerSession.objects.create(
            game=game,
            player=player,
            roster=game.get_emptier_team(),
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.AWAY
        )

    # update model that was indirectly updated
    # after it was updated, we can be sure that
    # plugin is aware that player is now member of
    # inGameTeam via new PlayerSession object
    await minestrike.update_game(game)

    # once player is recognized as member by backend we can trigger
    # join event
    await minestrike.join_game(game, player, session.roster, None, None)


@BukkitEventManager.on(PlayerLeaveGameEvent)
async def on_player_leave_game(minestrike: MineStrike, event: PlayerLeaveGameEvent):

    game = event.game
    player = event.player

    # don't do anything. Player will be rejoining same team
    # if there is an imbalance auto balance behaviour will be triggered in-game
    # sending request to change player roster


@BukkitEventManager.on(RequestPlayerTeamChangeEvent)
async def on_player_request_team_change(minestrike: MineStrike, event: RequestPlayerTeamChangeEvent):

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
