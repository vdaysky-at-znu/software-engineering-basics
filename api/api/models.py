import json
import random
from datetime import datetime
from enum import IntEnum
from typing import Union, Iterable, Optional

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.core import serializers
from django.db import models

from django.contrib.auth.models import AbstractUser, Permission

from api.constants import LocationCode


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

        def create_user(self, username, uuid, password):

            user = Player.objects.create(uuid=uuid, username=username)
            user.set_password(password)

            # default perms
            perm = Permission.objects.get(codename="can_create_teams")
            user.user_permissions.add(perm)

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

    @property
    def permissions(self):
        return list(self.user_permissions.all() | Permission.objects.filter(group__user=self))

    def verify(self):
        self.verified = True
        self.verified_at = datetime.now()

    def is_verified(self):
        return self.verified_at is not None

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
    """ Group of players inside particular game playing on the same side """

    # only for rosters
    name = models.CharField(null=True, max_length=20, default=None)

    starts_as_ct = models.BooleanField()
    is_ct = models.BooleanField()

    def get_current_team(self):
        if self.is_ct:
            return "CT"
        else:
            return "T"

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


class Game(models.Model):

    class Status(IntEnum):
        NOT_STARTED = 0
        STARTED = 1
        FINISHED = 2

    map = models.CharField(
        max_length=40,
        choices=(
               ('cache', 'Cache'),
               ('mirage', 'Mirage'),
               ('inferno', 'Inferno'),
               ('overpass', 'Overpass'),
               ('train', 'Train'),
               ('nuke', 'Nuke'),
           )
        )

    # Game status
    status = models.IntegerField(default=Status.NOT_STARTED)

    # Match
    match = models.ForeignKey("Match", models.CASCADE, null=True, related_name="games")

    # Teams
    team_a = models.OneToOneField(InGameTeam, on_delete=models.CASCADE, related_name="+")
    team_b = models.OneToOneField(InGameTeam, on_delete=models.CASCADE, related_name="+")

    # Plugins
    plugins = models.JSONField(default=list)

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

    def get_session(self, player):
        return PlayerSession.objects.filter(game=self, player=player).first()

    def has_plugin(self, plugin):
        return self.plugins and plugin in self.plugins


class Round(models.Model):
    """
        Represents a round in a game.
        Has context of absolute round number.
        If we want to rebuild score at halftime we
        have to rely on round number assuming half is 15 rounds.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    number = models.IntegerField()
    winner = models.ForeignKey(InGameTeam, null=True, on_delete=models.CASCADE)


class PlayerSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    roster = models.ForeignKey(InGameTeam, on_delete=models.CASCADE, related_name="sessions")

    @classmethod
    def get(cls, game, player):
        return PlayerSession.objects.filter(game=game, player=player).first()


class GamePlayerEvent(models.Model):
    """
        Represents a player event in game, like kill,
        death, bomb plant, defuse or anything else.
        This table can be used in many ways to analyze player activity
    """

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

    def create(self, turn):
        map_pick_process = MapPickProcess()
        map_pick_process.save()

        for map in ('Mirage', 'Inferno', 'Train', 'Dust II', 'Overpass', 'Nuke', 'Cache'):
            MapPick.objects.create(process=map_pick_process, map_name=map)

        return map_pick_process


class MapPickProcess(models.Model):

    finished = models.BooleanField(default=False)

    # 1 = ban, 2 = pick, 3 = default, 0 = null
    next_action = models.IntegerField(default=1)

    # team that has to make a decision
    turn = models.ForeignKey(Team, on_delete=models.CASCADE)

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

    team_one = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="+")
    team_two = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="+")

    name = models.CharField(max_length=100, null=True, default=None)
    start_date = models.DateTimeField()

    actual_start_date = models.DateTimeField(null=True, default=None)
    actual_end_date = models.DateTimeField(null=True, default=None)

    event = models.ForeignKey("Event", models.CASCADE, related_name="matches")
    map_count = models.IntegerField()

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

    def create(self, process, map_name, team=None, is_pick=None):

        pick = MapPick(
            process=process,
            map_name=map_name,
            selected_by=team,
            picked=is_pick,
        )
        pick.save()
        return pick


class MapPick(models.Model):
    """ Represents game map that was either picked, banned, or just present waiting to be picked or banned.
     Map pick process is initialized with 7 maps by default. """

    process = models.ForeignKey("MapPickProcess", models.CASCADE, related_name="maps")

    map_name = models.CharField(max_length=100)
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


class Article(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    images = models.JSONField(default=list)


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
