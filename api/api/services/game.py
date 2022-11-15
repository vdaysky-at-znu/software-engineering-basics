import logging
import random
from typing import Optional

from api.events.schemas.internal import PlayerLeftGame, PlayerRosterChange, PlayerStatusChange, PlayerJoinGame
from api.models import Match, InGameTeam, PlayerSession, Game, Player, MatchTeam, Map
from api.events.internal import internalHandler
from api.services.minestrike import MineStrike

PLUGIN_MAP = {
    Game.Mode.PUB: ['DefusalPlugin', 'WarmUpPlugin'],
    Game.Mode.DEATHMATCH: ['DeathmatchPlugin'],
    Game.Mode.COMPETITIVE: ['DefusalPlugin', 'WarmUpPlugin'],
    Game.Mode.DUELS: ['DuelPlugin', 'WarmUpPlugin'],
    Game.Mode.RANKED: ['RankedPlugin', 'WarmUpPlugin'],
}


@internalHandler.on("MapPickDone")
async def on_map_pick_done(match: Match, payload):

    print("Map pick done")

    game_meta = match.game_meta

    # create games with maps from map pick
    for map_pick in match.map_pick_process.picked.all().order_by("id"):

        print(f"Create game for {map_pick}")

        if match.team_one:
            igt_a = InGameTeam.from_match_team(match.team_one, is_ct=True)
        else:
            # Ranked games don't have teams but still use map picks.
            # TODO: perhaps I should do ranked magic here?
            #  it doesn't look right to create team for comp games here
            #  but for ranked separately
            igt_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)

        if match.team_two:
            igt_b = InGameTeam.from_match_team(match.team_two, is_ct=False)
        else:
            igt_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)

        game = match.games.create(
            map=map_pick.map_codename,
            team_a=igt_a,
            team_b=igt_b,
            plugins=PLUGIN_MAP[game_meta['mode']],
            mode=game_meta['mode'],
        )

        # only participants are allowed
        game.whitelist.add(*match.team_one.players.all(), *match.team_two.players.all())


def find_team_for_player(game: Game, player: Player) -> InGameTeam:
    """
    Find team for player in given game. Doesn't check if player can join the game,
    only tries its best to find a better option. Does consider game options, like
    team auto balance option.
    """

    match: Match = game.match

    roster = None

    # If player is supposed to participate in match, respect team choice
    if match:
        match_team: Optional[MatchTeam] = match.get_player_team(player)

        if match_team:
            roster = match_team.in_game_team

    # If roster wasn't found, see if player already was on team
    roster = roster or game.get_player_team(player)

    if not roster:
        # if still no luck, just put player on team with less players
        roster = game.get_emptier_team()
    else:
        # if roster was found, but it is overfilled,
        # put player on team with fewer players, unless config says otherwise
        team_overpopulated = roster.active_sessions().count() > game.get_emptier_team().active_sessions().count() + 1
        if game.get_config_var(Game.ConfigField.AUTO_TEAM_BALANCE) and team_overpopulated:
            roster = game.get_emptier_team()

    return roster


def team_auto_balance(game: Game) -> bool:

    team_a = game.team_a
    team_b = game.team_b

    if team_a.players.count() > team_b.players.count() + 1:
        # take random player from team A and put them to team B
        player = random.choice(team_a.players.all())
        team_a.players.remove(player)
        team_b.players.add(player)
        return True

    elif team_b.players.count() > team_a.players.count() + 1:
        # take random player from team B and put them to team A
        player = random.choice(team_b.players.all())
        team_b.players.remove(player)
        team_a.players.add(player)
        return True

    return False


async def leave_active_game(player: Player):
    """ Make player leave game they are currently are in"""
    session = player.get_active_session()
    if not session:
        return

    logging.info(f"Player {player} leaving game {session.game}...")

    session.state = PlayerSession.State.AWAY
    session.save()

    # handle internally
    await internalHandler.propagate_event(event=PlayerLeftGame(session=session), sender=session)

    logging.info(f"Propagate game leave to Bukkit...")

    # explicitly tell Bukkit that player left
    await MineStrike(1).leave_game(game=session.game, player=player)

    logging.info(f"Player {player} left game {session.game}")


async def join_game(game: Game, player: Player, status: int, roster):
    """
        Make player join given game.
    """

    logging.info(f"Joining game {game} with {player} as {status}")

    if status == PlayerSession.Status.SPECTATOR and roster is not None:
        raise ValueError("Player can't spectate and be in a roster")

    active_game: Optional[Game] = player.get_active_game()

    if active_game:
        logging.info(f"Player {player} is currently in game {active_game}")
        await leave_active_game(player)

    # player might have idle session already
    session = PlayerSession.objects.filter(
        game=game,
        player=player,
    ).first()

    # Player doesn't have a session yet. Just create a new one
    if not session:
        session = PlayerSession.objects.create(
            game=game,
            player=player,
            roster=roster,
            status=status,
            state=PlayerSession.State.IN_GAME
        )
    # player had session but in different roster
    else:
        if session.roster != roster:
            old_roster = session.roster
            session.roster = roster
            session.save()

            await internalHandler.propagate_event(
                event=PlayerRosterChange(session=session, old_roster=old_roster, new_roster=roster),
                sender=session
            )

        # player had a session but in different status
        if session.status != status:
            old_status = session.status
            session.status = status
            session.save()

            await internalHandler.propagate_event(
                event=PlayerStatusChange(session=session, old_status=old_status, new_status=status),
                sender=session
            )

    logging.info(f"Player {player} now has updated session {session}")

    # since we know player wasn't in game, we have to change state
    session.state = PlayerSession.State.IN_GAME
    session.save()

    # update model that was indirectly updated
    # after it was updated, we can be sure that
    # plugin is aware that player is now member of
    # inGameTeam via new PlayerSession object
    r = await MineStrike(1).update_game(game)
    print(f"Response from BUKKIT: {r}")

    logging.info(f"Propagating internally")

    # handle internally
    await internalHandler.propagate_event(
        event=PlayerJoinGame(session=session),
        sender=session
    )

    logging.info(f"Player {player} joining game {game}...")

    # explicitly tell Bukkit that player joined
    await MineStrike(1).join_game(game=session.game, player=player, team=roster)

    logging.info(f"Player {player} joined game {game}")


async def create_game(map: Map, mode: int):
    """
        Create game with given map and mode.
    """
    team_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)
    team_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)

    game = Game.objects.create(
        map=map,
        mode=mode,
        plugins=PLUGIN_MAP[mode],
        status=Game.Status.NOT_STARTED,
        team_a=team_a,
        team_b=team_b,
    )

    return game


async def create_pub(map_name=None):
    """ Create new pub game """

    if not map_name:
        map_name = random.choice(['MIRAGE'])

    team_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)
    team_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)

    game = Game.objects.create(
        mode=Game.Mode.PUB,
        team_a=team_a,
        team_b=team_b,
        status=Game.Status.NOT_STARTED,
        plugins=PLUGIN_MAP[Game.Mode.PUB],
        map=map_name
    )

    return game


async def create_deathmatch(map_name=None):
    """ Create new deathmatch game """

    if not map_name:
        map_name = random.choice(['MIRAGE'])

    team_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)
    team_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)

    game = Game.objects.create(
        mode=Game.Mode.DEATHMATCH,
        team_a=team_a,
        team_b=team_b,
        status=Game.Status.NOT_STARTED,
        plugins=PLUGIN_MAP[Game.Mode.DEATHMATCH],
        map=map_name
    )

    return game


async def create_duels(map_name=None):
    """ Create new duels game """

    if not map_name:
        map_name = random.choice(['MIRAGE'])

    team_a = InGameTeam.objects.create(starts_as_ct=True, is_ct=True)
    team_b = InGameTeam.objects.create(starts_as_ct=False, is_ct=False)

    game = Game.objects.create(
        mode=Game.Mode.DUELS,
        team_a=team_a,
        team_b=team_b,
        status=Game.Status.NOT_STARTED,
        plugins=PLUGIN_MAP[Game.Mode.DUELS],
        map=map_name
    )


    return game
