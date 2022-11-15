from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from enum import IntEnum
from typing import Union, Iterable, Optional, List

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from django.contrib.auth.models import AbstractUser, Permission
from django.db.models import Q

from api.constants import LocationCode
from api.events.schemas.internal import PlayerLeftGame, PlayerRosterChange, PlayerStatusChange, PlayerJoinGame


class Team(models.Model):
    """ Competitive roster of players """

    short_name = models.CharField(max_length=10, unique=True, null=False)
    full_name = models.CharField(max_length=20, unique=True, null=False)
    active = models.BooleanField(default=True)
    location = models.IntegerField(default=0)
    elo = models.IntegerField(default=0)
    owner = models.ForeignKey('Player', models.CASCADE, null=False, related_name="teams")


class Player(AbstractUser):
    """ Player in game / user on website """

    class UserManager(BaseUserManager):

        def create_user(self, username, uuid, password, role):

            user = Player.objects.create(uuid=uuid, username=username, role=role)
            user.set_password(password)

            user.save()
            return user

        def create_superuser(self, uuid, password):
            user = Player.objects.create(
                uuid=uuid,
            )

            user.set_password(password)

            user.is_superuser = True
            user.save()
            return user

    uuid = models.UUIDField(unique=True, null=False)
    team = models.ForeignKey(Team, models.SET_NULL, default=None, null=True, related_name="players")
    role = models.ForeignKey('Role', models.CASCADE, null=False, related_name="players")
    elo = models.IntegerField(default=0)
    location_code = models.CharField(default=LocationCode.NONE, max_length=20)
    verified_at = models.DateTimeField(null=True, default=None)

    in_server = models.BooleanField(default=False)

    def has_perm(self, perm, obj=None):
        return self.role is not None and self.role.has_perm(perm)

    @property
    def permissions(self):
        return list(self.user_permissions.all() | Permission.objects.filter(group__user=self))

    def verify(self):
        self.verified = True
        self.verified_at = datetime.now()

    def is_verified(self):
        return self.verified_at is not None

    def get_owned_team(self):
        return self.teams.first()

    def get_active_session(self) -> Optional[PlayerSession]:
        return PlayerSession.objects.filter(state=PlayerSession.State.IN_GAME, player=self).first()

    def get_active_game(self) -> Optional[Game]:
        session = self.get_active_session()
        if not session:
            return

        return session.game

    def can_join_game(self, game: Game, roster: Optional[InGameTeam], status: int) -> bool:
        """ Check whether this player can join given game """

        # Player is not whitelisted
        if game.whitelist.count() != 0 and not game.whitelist.filter(id=self.id).exists():
            logging.info("Player is not whitelisted")
            return False

        # Player is blacklisted
        if game.blacklist.filter(id=self.id).exists():
            logging.info("Player is blacklisted")
            return False

        participants = len(game.get_online_sessions(status=PlayerSession.Status.PARTICIPATING))
        max_participants = game.get_config_var(Game.ConfigField.MAX_PLAYERS)

        # There are no free slots
        if status == PlayerSession.Status.PARTICIPATING and participants >= max_participants:
            logging.info("No free slots")
            return False

        # Player can't be a coach in this in-game roster
        if status == PlayerSession.Status.COACH and not self.can_coach(roster):
            logging.info("Can't be a coach")
            return False

        return True

    def can_coach(self, roster: Optional[InGameTeam]) -> bool:

        if not roster:
            return False

        # Game is not match-based
        if roster.match_team is None:
            return False

        # Player is not a member of MatchTeam
        if not roster.match_team.players.filter(id=self.id).exists():
            return False

        return True

    objects = UserManager()

    class Meta:
        permissions = (
            ("team_owner", "Owns team"),
            ("team_leader", "Is team leader"),
            ("can_create_events", "Can create Events"),
            ("can_create_players", "Can create Players"),
            ("can_create_teams", "Can create Teams"),
            ("can_create_matches", "Can create Match")
        )


class Invite(models.Model):
    """ Invite sent to player to join a team """

    player = models.ForeignKey(Player, models.CASCADE, related_name="invites")
    team = models.ForeignKey(Team, models.CASCADE)

    status = models.IntegerField(null=True, default=None)

    @property
    def declined(self):
        return self.status == 0

    @property
    def accepted(self):
        return self.status == 1

    @declined.setter
    def declined(self, v):
        self.status = 0 if v is True else None

    @accepted.setter
    def accepted(self, v):
        self.status = 1 if v is True else None


# 2 instances per game
class InGameTeam(models.Model):
    """
        Group of players inside particular game playing on the same side.
        Can contain AWAY players.
    """

    # only for team-ish entities (produced from Team or MatchTeam)
    name = models.CharField(null=True, max_length=32, default=None)

    # reference to MatchTeam that created this InGameTeam, if exists
    # for Ranked/Competitive games (ones having Match) there are usually
    # MatchTeam objects that define who can get into this match.
    match_team = models.OneToOneField('MatchTeam', on_delete=models.CASCADE, null=True, related_name='in_game_team')

    starts_as_ct = models.BooleanField()
    is_ct = models.BooleanField()

    def get_current_team(self):
        if self.is_ct:
            return "CT"
        else:
            return "T"

    def active_sessions(self):
        return self.sessions.filter(state=PlayerSession.State.IN_GAME)

    def get_players(self):
        return [x.player for x in self.sessions.all()]

    def award_elo(self, elo):
        for player in self.get_players():
            player.elo = player.elo + elo
            player.save()

    def deduct_elo(self, elo):
        for player in self.get_players():
            player.elo = max(0, player.elo - elo)
            player.save()

    @property
    def game(self):
        return Game.objects.get(Q(team_a=self) | Q(team_b=self))

    @classmethod
    def from_match_team(cls, team: MatchTeam, is_ct: bool):
        team_1 = InGameTeam.objects.create(
            name=team.name,
            starts_as_ct=is_ct,
            is_ct=is_ct,
            match_team=team
        )

        return team_1


class MatchTeam(models.Model):
    """
        Player set that can join in-game team.
    """

    # NOTE:
    # match is accessible through `match` reverse relation
    # in-game team is accessible through `in_game_team`

    # display name
    name = models.CharField(max_length=32, null=True, default=None)

    # Real team this match team is based on
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL)

    players = models.ManyToManyField(Player)

    @classmethod
    def from_team(cls, team: Team):
        return MatchTeam.objects.create(
            name=team.short_name,
            team=team,
        )

    @property
    def match(self):
        return self.match_one or self.match_two


class MapTag(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Map(models.Model):
    display_name = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

    tags = models.ManyToManyField(MapTag)

    class Tag:
        ACTIVE_POOL = 1

    @classmethod
    def with_tag(cls, *tag_ids):
        return cls.objects.filter(tags__in=tag_ids).distinct()


class Game(models.Model):

    class Status(IntEnum):
        NOT_STARTED = 0
        STARTED = 1
        FINISHED = 2

    class Mode:
        COMPETITIVE = 1
        PUB = 2
        DEATHMATCH = 3
        DUELS = 4
        RANKED = 5

        @staticmethod
        def to_code(name):
            return getattr(Game.Mode, name.upper(), None)

    class ConfigField:
        MAX_PLAYERS = "MAX_PLAYERS"
        AUTO_TEAM_BALANCE = "AUTO_TEAM_BALANCE"

    map = models.ForeignKey(Map, models.CASCADE)

    # Game status
    status = models.IntegerField(default=Status.NOT_STARTED)

    # Match
    match = models.ForeignKey("Match", models.CASCADE, null=True, related_name="games")

    # Teams
    team_a = models.OneToOneField(InGameTeam, on_delete=models.CASCADE, related_name="+")
    team_b = models.OneToOneField(InGameTeam, on_delete=models.CASCADE, related_name="+")

    winner = models.ForeignKey(InGameTeam, models.SET_NULL, null=True, related_name="+")

    # Plugins
    plugins = models.JSONField(default=list)

    mode = models.IntegerField()

    config_overrides = models.JSONField(default=dict)

    # Whitelist
    whitelist = models.ManyToManyField(Player, related_name="whitelisted_games")
    blacklist = models.ManyToManyField(Player, related_name="blacklisted_games")

    def get_default_config(self):
        return {
            Game.Mode.PUB: {
                Game.ConfigField.MAX_PLAYERS: 10,
                Game.ConfigField.AUTO_TEAM_BALANCE: True,
            },
            Game.Mode.RANKED: {
                Game.ConfigField.MAX_PLAYERS: 10,
                Game.ConfigField.AUTO_TEAM_BALANCE: False,
            },
            Game.Mode.DUELS: {
                Game.ConfigField.MAX_PLAYERS: 10,
                Game.ConfigField.AUTO_TEAM_BALANCE: True,
            },
            Game.Mode.DEATHMATCH: {
                Game.ConfigField.MAX_PLAYERS: 10,
                Game.ConfigField.AUTO_TEAM_BALANCE: False,
            },
            Game.Mode.COMPETITIVE: {
                Game.ConfigField.MAX_PLAYERS: 10,
                Game.ConfigField.AUTO_TEAM_BALANCE: False,
            }
        }[self.mode]

    def get_config_var(self, name) -> int:
        if name in self.config_overrides:
            return self.config_overrides[name]

        return self.get_default_config()[name]

    def get_online_sessions(self, status: int = None) -> List[PlayerSession]:
        q = self.sessions.filter(state=PlayerSession.State.IN_GAME)

        if status:
            q = q.filter(status=status)
        return q

    def get_player_team(self, player: Player):
        for team in [self.team_a, self.team_b]:
            if player in team.get_players():
                return team

    @property
    def is_started(self):
        return self.status == self.Status.STARTED

    @property
    def is_finished(self):
        return self.status == self.Status.FINISHED

    def get_emptier_team(self):
        if self.team_a.sessions.count() < self.team_b.sessions.count():
            return self.team_a
        return self.team_b

    def get_team(self, short_name):
        if self.team_a.get_current_team() == short_name:
            return self.team_a

    def get_session(self, player) -> PlayerSession:
        return PlayerSession.objects.filter(game=self, player=player).first()

    def has_plugin(self, plugin):
        return self.plugins and plugin in self.plugins

    @property
    def score_a(self):
        return Round.objects.filter(game=self, winner=self.team_a).count()

    @property
    def score_b(self):
        return Round.objects.filter(game=self, winner=self.team_b).count()


class Round(models.Model):
    """
        Represents a round in a game.
        Has context of absolute round number.
        If we want to rebuild score at halftime we
        have to rely on round number assuming half is 15 rounds.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    number = models.IntegerField()
    winner = models.ForeignKey(InGameTeam, null=True, on_delete=models.CASCADE)


class PlayerSession(models.Model):

    class Status:
        """
            Player's status in this game.
            Player can be a coach, can spectate
            or can participate in a game.
        """
        PARTICIPATING = 1
        COACH = 2
        SPECTATOR = 3

    class State:
        """
            Player game session state.
            Even after quitting the game itself player still might be in-game,
            which ensures that player is going to get in that game automatically after rejoin
        """
        IN_GAME = 1  # player is associated with this game
        AWAY = 2  # player once was in the game but left

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    roster = models.ForeignKey(InGameTeam, null=True, on_delete=models.CASCADE, related_name="sessions")

    status = models.IntegerField()
    state = models.IntegerField()

    @classmethod
    def get(cls, game, player):
        return PlayerSession.objects.filter(game=game, player=player).first()


class GamePlayerEvent(models.Model):
    """
        Represents a player event in game, like kill,
        death, bomb plant, defuse or anything else.
        This table can be used in many ways to analyze player activity
    """

    class Type:
        KILL = "KILL"
        DEATH = "DEATH"
        ASSIST = "ASSIST"
        BOMB_PLANT = "BOMB_PLANT"
        BOMB_DEFUSE = "BOMB_DEFUSE"

    # Event name
    event = models.CharField(max_length=255)

    # Game
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    # Player
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # Round
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    # Meta
    meta = models.JSONField(default=dict)

    # Is player CT
    is_ct = models.BooleanField()  # T / CT

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)


class MapPickProcessManager(models.Manager):

    def create(self):
        map_pick_process = MapPickProcess()
        map_pick_process.save()

        for map in Map.with_tag(Map.Tag.ACTIVE_POOL):
            MapPick.objects.create(process=map_pick_process, map=map)

        return map_pick_process


class MapPickProcess(models.Model):

    class Action:
        PICK = 2
        BAN = 1
        NULL = 0

    finished = models.BooleanField(default=False)

    # 1 = ban, 2 = pick, 3 = default, 0 = null
    next_action = models.IntegerField(default=1)

    picker_a = models.ForeignKey(Player, models.SET_NULL, null=True, related_name="+")
    picker_b = models.ForeignKey(Player, models.SET_NULL, null=True, related_name="+")

    # player that has to make a decision
    turn = models.ForeignKey(Player, null=True, on_delete=models.CASCADE)

    def other_picker(self, picker):
        if picker == self.picker_a:
            return self.picker_b
        elif picker == self.picker_b:
            return self.picker_a
        raise ValueError(f"Picker is not in match")

    @property
    def last_action(self):
        return self.maps.order_by('-id').first()

    @property
    def picked(self):
        return self.maps.filter(picked=True)

    @property
    def banned(self):
        return self.maps.filter(picked=False)

    objects = MapPickProcessManager()


def new_map_pick_process():
    return MapPickProcess.objects.create()


class Match(models.Model):

    def other_team(self, team):
        if team == self.team_one:
            return self.team_two
        elif team == self.team_two:
            return self.team_one
        raise ValueError(f"<team {team.short_name}/> is not in <match id={self.id} />")

    def get_random_team(self):
        return random.choice([self.team_one, self.team_two])

    def get_player_team(self, player: Player) -> Optional[MatchTeam]:
        if self.team_one and self.team_one.players.filter(id=player.id).exists():
            return self.team_one

        if self.team_two and self.team_two.players.filter(id=player.id).exists():
            return self.team_two

        return None

    # set of players that *can* participate in game on behalf of a team at the moment of match creation
    # NOTE: Django is stupid, and thinks there would be a clash between the two reverse lookups.
    # if you ever need to run a migration, run it with --skip-checks flag.
    team_one = models.OneToOneField(MatchTeam,  on_delete=models.SET_NULL, null=True, related_name="match_one")
    team_two = models.OneToOneField(MatchTeam,  on_delete=models.SET_NULL, null=True, related_name="match_two")

    name = models.CharField(max_length=100, null=True, default=None)
    start_date = models.DateTimeField()

    actual_start_date = models.DateTimeField(null=True, default=None)
    actual_end_date = models.DateTimeField(null=True, default=None)

    event = models.ForeignKey("Event", models.CASCADE, null=True, default=None, related_name="matches")
    map_count = models.IntegerField()

    # data that helps to construct game instances
    game_meta = models.JSONField(null=False)

    map_pick_process = models.OneToOneField(
        MapPickProcess,
        models.CASCADE,
        default=new_map_pick_process,
        related_name="match"
    )


class Event(models.Model):
    """ Competitive event / tournament """
    name = models.CharField(max_length=100)
    start_date = models.DateField()


class MapPickManager(models.Manager):

    def create(self, process, map: Map, team=None, is_pick=None):

        pick = MapPick(
            process=process,
            map=map,
            selected_by=team,
            picked=is_pick,
        )
        pick.save()
        return pick


class MapPick(models.Model):
    """ Represents game map that was either picked, banned, or just present waiting to be picked or banned.
     Map pick process is initialized with 7 maps by default. """

    process = models.ForeignKey("MapPickProcess", models.CASCADE, related_name="maps")

    map = models.ForeignKey(Map, models.SET_NULL, null=True, related_name="+")
    selected_by = models.ForeignKey(Team, models.CASCADE, null=True, default=None)
    picked = models.BooleanField(null=True, default=None)
    objects = MapPickManager()

    def was_selected(self):
        return self.selected_by is not None


class PlayerPermission(models.Model):
    name = models.CharField(max_length=100)


class Role(models.Model):
    name = models.CharField(max_length=100)
    tab_prefix = models.CharField(max_length=100)
    tab_color = models.CharField(max_length=100)
    chat_prefix = models.CharField(max_length=100)
    chat_suffix = models.CharField(max_length=100)
    chat_color = models.CharField(max_length=100)
    chat_message_color = models.CharField(max_length=100)
    team_override_color = models.BooleanField(max_length=100)
    permissions = models.ManyToManyField(PlayerPermission, related_name="permissions")

    def has_perm(self, perm):
        for has_perm in self.permissions.all():
            parts_present = has_perm.name.split(".")
            parts_required = perm.split(".")

            # present permission is more specific than required
            if len(parts_present) > len(parts_required):
                continue

            # iterate both lists and check if they match
            for pres, req in zip(parts_present, parts_required):
                if pres != req:
                    if pres == "*":
                        return True
                    break
            else:
                return True

        return False


class PlayerQueue(models.Model):

    class Type:
        RANKED = 1

    type = models.IntegerField()
    meta = models.JSONField(default=dict)

    locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, default=None)

    confirmed = models.BooleanField(default=False)

    # once queue is full, map picking will start
    captain_a = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, default=None, related_name="+")
    captain_b = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, default=None, related_name="+")

    # once queue is full, it will be associated with a match.
    # usually Bo1 will be played, but still match is preferred because it has all map pick features
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, default=None)

    players = models.ManyToManyField(Player, related_name="+")

    confirmed_players = models.ManyToManyField(Player, related_name="+")

    def join(self, player: Player) -> bool:
        if self.has(player):
            return False

        self.players.add(player)
        return True

    def has(self, player: Player):
        """ Checks if player is in THIS queue already """
        return self.players.filter(id=player.id).exists()

    def leave(self, player: Player) -> bool:
        if not self.has(player):
            return False

        self.players.remove(player)
        return True

    def has_confirmed(self, player: Player):
        return self.confirmed_players.filter(id=player.id).exists()

    def unlock(self):
        self.locked = False
        self.locked_at = None
        self.save()

    def lock(self):
        self.locked = True
        self.locked_at = datetime.now()
        self.save()

    def confirm(self, player: Player):
        if self.has_confirmed(player):
            return False

        self.confirmed_players.add(player)
        return True

    def unconfirm(self):
        self.confirmed_players.clear()


class Post(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    images = models.JSONField(default=list)
    header_image = models.CharField(max_length=1024, null=True)


class AuthSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, default=None)
    session_key = models.CharField(max_length=64)
    data = models.JSONField(default=dict)

    def set_data(self, **data):
        self.data = {**self.data, **data}
        self.save()

    def get_data(self, key):
        return self.data.get(key)

    @classmethod
    def create(cls, player: Optional[Player]):
        return AuthSession.objects.create(
            player=player,
            session_key="".join(
                [
                    random.choice(
                        list("qwertyuiopasdfghjklzxcvbnm1234567890")
                    )
                    for _ in range(64)
                ]
            )
        )

    @classmethod
    def log_out(cls, player):
        AuthSession.objects.filter(player=player).delete()
        return
