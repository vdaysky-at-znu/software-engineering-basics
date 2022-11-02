from typing import Optional

from api.events.schemas.internal import PlayerLeftGame, PlayerRosterChange, PlayerStatusChange, PlayerJoinGame
from api.models import Match, InGameTeam, PlayerSession, Game, Player, MatchTeam
from api.events.internal import internalHandler
from api.services.minestrike import MineStrike


@internalHandler.on("MapPickDone")
async def on_map_pick_done(match: Match, payload):

    print("Map pick done")

    game_meta = match.game_meta

    plugin_map = {
        Game.Mode.PUB: ['DefusalPlugin', 'WarmupPlugin'],
        Game.Mode.DEATHMATCH: ['DeathmatchPlugin'],
        Game.Mode.COMPETITIVE: ['CompetitivePlugin'],
        Game.Mode.DUELS: ['DuelPlugin'],
        Game.Mode.RANKED: ['RankedPlugin'],
    }

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
            plugins=plugin_map[game_meta['mode']],
            mode=game_meta['mode'],
        )

        # only participants are allowed
        game.whitelist.add(*match.team_one.players.all(), *match.team_two.players.all())


def find_team_for_player(game: Game, player: Player):
    match: Match = game.match

    roster = None

    if match:
        match_team: Optional[MatchTeam] = match.get_player_team(player)

        if match_team:
            roster = match_team.in_game_team

    if not roster:
        roster = game.get_emptier_team()

    return roster


async def leave_active_game(player: Player):
    """ Make player leave game they are currently are in"""
    session = player.get_active_session()
    if not session:
        return

    session.state = PlayerSession.State.AWAY
    session.save()

    # handle internally
    await internalHandler.propagate_event(event=PlayerLeftGame(session=session), sender=session)

    # explicitly tell Bukkit that player left
    await MineStrike(1).leave_game(game=session.game, player=player)


async def join_game(game: Game, player: Player, status: int, roster):
    """
        Make player join given game.
    """

    if status == PlayerSession.Status.SPECTATOR and roster is not None:
        raise ValueError("Player can't spectate and be in a roster")

    active_game: Optional[Game] = player.get_active_game()

    if active_game:
        await leave_active_game(player)

    # player might have idle session already
    session = PlayerSession.objects.filter(
        game=game,
        player=player,
    ).first()

    # Player doesn't have a session yet. Just create a new one
    if not session:
        PlayerSession.objects.create(
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

    # since we know player wasn't in game, we have to change state
    session.state = PlayerSession.State.IN_GAME
    session.save()

    # handle internally
    await internalHandler.propagate_event(
        event=PlayerJoinGame(session=session),
        sender=session
    )

    # explicitly tell Bukkit that player joined
    await MineStrike(1).join_game(game=session.game, player=player, team=roster, status=status)
