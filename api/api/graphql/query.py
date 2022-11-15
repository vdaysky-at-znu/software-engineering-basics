import inspect
import json
from typing import List, TypeVar, Generic, get_args, Type, Tuple, Optional

from ariadne import QueryType, make_executable_schema, ObjectType
from django.db.models import Q, Sum, Count, F

from api.graphql.virtual import TableManager, VirtualTable, Table, computed, PaginatedTable, VirtualGenericTable
from api.models import Player, Team, Role, PlayerPermission, Game, InGameTeam, PlayerSession, Event, Match, Invite, \
    MapPickProcess, MapPick, GamePlayerEvent, PlayerQueue, MatchTeam, Post, Map

tableManager = TableManager()

T = TypeVar('T')


@tableManager.type
class Page(Generic[T], VirtualGenericTable):
    count: int
    items: List[T]

    def __init__(self, count: int, items: List[T]):
        self.count = count
        self.items = items


@tableManager.table
class ArticleTable(Table[Post]):
    id: int
    title: str
    subtitle: str
    text: str
    author_id: int
    date: str
    header_image: str


@tableManager.table
class EventTable(Table[Event]):
    id: int
    name: str
    start_date: str

    @computed
    def match_ids(self, page: int = 0, count: int = 10) -> Page[int]:
        return Page(self.matches.count(), self.matches.values_list('id', flat=True)[page * count:page * count + count])


@tableManager.table
class PlayerTable(Table[Player]):
    id: int
    username: str
    uuid: str
    elo: int
    role_id: int
    team_id: int
    owned_team_id: int
    in_server: bool

    @computed
    def game_id(self) -> Optional[int]:
        game = self.get_active_game()
        if game:
            return game.id

    @computed
    def on_website(self) -> bool:
        from api.consumers import WsPool
        conn = WsPool.get_player_conn(self)
        return conn is not None


@tableManager.table
class RoleTable(Table[Role]):
    id: int
    name: str

    tab_prefix: str
    tab_color: str
    chat_prefix: str
    chat_suffix: str
    chat_color: str
    chat_message_color: str
    team_override_color: bool

    @computed
    def permission_ids(self) -> List[int]:
        return self.permissions.values_list('id', flat=True)


@tableManager.table
class PermissionTable(Table[PlayerPermission]):
    id: int
    name: str


@tableManager.table
class TeamTable(Table[Team]):
    id: int
    elo: int
    owner_id: int

    short_name: str
    full_name: str
    location_code: str

    @computed
    def member_ids(self, page: int = 0, count: int = 10) -> Page[int]:
        _all = Player.objects.filter(team_id=self.id)
        return Page(_all.count(), [player.id for player in _all[page * count:page * count + count]])


@tableManager.table
class MatchTable(Table[Match]):
    id: int
    event_id: int
    team_one_id: int
    team_two_id: int
    name: str
    start_date: str
    map_count: int
    map_pick_process_id: int

    @computed
    def game_ids(self, page: int = 0, count: int = 10) -> Page[int]:
        _all = Game.objects.filter(match_id=self.id)
        return Page(_all.count(), [game.id for game in _all[page * count:page * count + count]])


@tableManager.table
class MapTable(Table[Map]):
    id: int
    name: str
    display_name: str


@tableManager.table
class MatchTeamTable(Table[MatchTeam]):
    id: int
    team_id: int
    name: str
    in_game_team_id: int

    @computed(paginate=True)
    def player_ids(self) -> List[int]:
        return self.players.all()


@tableManager.table(queryable=False)
class Config(VirtualTable):
    overrides: str

    @classmethod
    def resolve(cls, __parent=None, **args):
        return cls(game=__parent)

    def __init__(self, game: Game):
        self.overrides = json.dumps({
            "something": 1
        })


@tableManager.table
class GameTable(Table[Game]):
    id: int
    map_id: int
    is_finished: bool
    is_started: bool
    match_id: int
    team_a_id: int
    team_b_id: int
    config: Config
    plugins: List[str]
    score_a: int
    score_b: int

    @computed
    def session_ids(self) -> List[int]:
        return [s.id for s in self.sessions.all()]

    @computed
    def blacklist_ids(self) -> List[int]:
        return [p.id for p in self.blacklist.all()]

    @computed
    def whitelist_ids(self) -> List[int]:
        return [p.id for p in self.whitelist.all()]


@tableManager.table
class PlayerSessionTable(Table[PlayerSession]):
    id: int
    player_id: int
    game_id: int
    roster_id: int


@tableManager.table
class MapPickProcessTable(Table[MapPickProcess]):
    id: int
    finished: bool
    next_action: int
    turn_id: int

    @computed
    def match_id(self) -> int:
        return self.match.id

    @computed
    def map_ids(self, page: int = 0, size: int = 10) -> Page[int]:
        return Page(self.maps.count(), self.maps.values_list('id', flat=True)[page * size:page * size + size])


@tableManager.table
class MapPickTable(Table[MapPick]):
    id: int
    map_name: str
    selected_by_id: int
    picked: bool
    process_id: int


@tableManager.table
class InGameTeamTable(Table[InGameTeam]):
    id: int
    name: str
    starts_as_ct: bool
    is_ct: bool

    @computed
    def player_ids(self) -> List[int]:
        return [p.player.id for p in self.sessions.all()]


@tableManager.table
class GamePlayerEventTable(Table[GamePlayerEvent]):
    id: int
    game_id: int
    player_id: int
    event: str
    round_id: int
    is_ct: bool


@tableManager.table
class FftPlayer(VirtualTable):
    id: int
    uuid: str
    invited: bool
    username: str

    def __init__(self, player_id: int, team_id: int):
        player = Player.objects.get(id=player_id)

        self.id = player.id
        self.uuid = player.uuid
        self.username = player.username

        team = Team.objects.get(id=team_id)
        self.invited = Invite.objects.filter(player=player, team=team).exists()


@tableManager.table
class FftPlayerId(VirtualTable):
    player_id: int
    team_id: int

    def __init__(self, player_id: int, team_id: int):
        self.player_id = player_id
        self.team_id = team_id


@tableManager.table
class FftPlayerView(VirtualTable):

    @computed
    def player_ids(self, page: int = 0, size: int = 10) -> Page[FftPlayerId]:
        _all = Player.objects.filter(team=None)
        return Page(
            _all.count(),
            [FftPlayerId(player.id, self.team_id) for player in _all[page * size:page * size + size]]
        )

    def __init__(self, team_id: int):
        self.team_id = team_id


@tableManager.table
class ManyToOne(PaginatedTable[int]):

    def __init__(self, model: str, page: int, size: int, id: int = None, field: str = None):
        from django.apps import apps

        if id is None and field is None:
            model = apps.get_model('api', model).objects.all()
            ids = [m.id for m in model]
        else:
            model = apps.get_model('api', model).objects.get(id=id)
            ids = [getattr(obj, 'id') for obj in getattr(model, field).all()]

        super().__init__(ids, page, size)


@tableManager.table
class PlayerPerformanceAggregatedView(VirtualTable):
    """ Player stats optionally inside a game """
    player_id: int
    kills: int
    deaths: int
    assists: int
    hs: float

    def __init__(self, player_id: int = None, game_id: int = None):
        self.player_id = player_id
        self.game_id = game_id

        print(f"get player performance for {player_id} in {game_id}")

        stats = GamePlayerEvent.objects.all()

        if self.player_id:
            stats = stats.filter(player_id=self.player_id)

        if self.game_id:
            stats = stats.filter(game_id=self.game_id)

        for s in stats:
            print(s.player, s.event)

        aggregated_stats = stats.filter(player_id=player_id).aggregate(
            kills=Count('id', filter=Q(event='KILL')),
            deaths=Count('id', filter=Q(event='DEATH')),
            assists=Count('id', filter=Q(event='ASSIST')),
            hs=Count('id', filter=Q(meta__hs=True))
        )

        self.player_id = player_id
        self.kills = aggregated_stats['kills']
        self.deaths = aggregated_stats['deaths']
        self.assists = aggregated_stats['assists']

        headshots = aggregated_stats['hs']
        self.hs = (headshots / self.kills) if headshots else 0
        self.hs *= 100
        self.hs = round(self.hs, 2)

    @computed
    def games_played(self) -> int:
        # temporary, possible to abuse by spamming sessions
        return PlayerSession.objects.filter(player_id=self.player_id).count()

    @computed
    def games_won(self) -> int:
        return PlayerSession.objects.filter(player_id=self.player_id, roster=F('game__winner')).count()

    @computed
    def ranked_games_played(self) -> int:
        return PlayerSession.objects.filter(player_id=self.player_id, game__plugins__contains='RankedPlugin').count()

    @computed
    def ranked_games_won(self) -> int:
        return PlayerSession.objects.filter(player_id=self.player_id, roster=F('game__winner'), game__plugins__contains='RankedPlugin').count()


@tableManager.table
class PlayerStatId(VirtualTable):
    player_id: int
    game_id: int

    def __init__(self, player_id: int, game_id: int):
        self.player_id = player_id
        self.game_id = game_id


@tableManager.table
class GameStatsView(VirtualTable):

    def __init__(self, game_id: int = None, in_game_team_id: int = None, player_id: int = None):
        self.game_id = game_id
        self.in_game_team_id = in_game_team_id
        self.player_id = player_id

    @computed(paginate=True)
    def stats(self) -> List[PlayerStatId]:

        # players to retrieve stats for
        players = set()

        if self.player_id:
            players.add(self.player_id)

        if self.in_game_team_id:
            team: InGameTeam = InGameTeam.objects.get(id=self.in_game_team_id)
            players.update(team.sessions.all().values_list('player_id', flat=True))

        if self.game_id:
            for team in InGameTeam.objects.filter(game_id=self.game_id):
                players.update(team.sessions.all().values_list('player_id', flat=True))

        return [PlayerStatId(player, self.game_id) for player in players]


@tableManager.table
class TopTeamView(TeamTable):

    @classmethod
    def get_type_name(cls):
        return 'TopTeamView'

    @classmethod
    def get_constructor_args(cls) -> List[Tuple[str, Type]]:
        return [('order_by', str)]

    @classmethod
    def resolve(cls, __parent=None, order_by: str = '-elo'):
        return Team.objects.all().order_by(order_by).first()


@tableManager.table
class TopPlayersView(VirtualTable):

    def __init__(self, order_by: str):
        self.order_by = order_by

    @computed(paginate=True)
    def player_ids(self) -> List[int]:
        return Player.objects.all().order_by(self.order_by)


@tableManager.table
class PubsView(VirtualTable):
    """ View of all games that don't have any plugins and can be joined by anyone """

    def __init__(self):
        pass

    @computed(paginate=True)
    def game_ids(self) -> List[int]:
        return Game.objects.filter(mode=Game.Mode.PUB).exclude(status=Game.Status.FINISHED).values_list('id', flat=True)

    @computed
    def online_player_count(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.PUB,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()


@tableManager.table
class DeathMatchView(VirtualTable):

    def __init__(self):
        pass

    @computed(paginate=True)
    def game_ids(self) -> List[int]:
        return Game.objects.filter(mode=Game.Mode.DEATHMATCH).exclude(status=Game.Status.FINISHED).values_list('id', flat=True)

    @computed
    def online_player_count(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.DEATHMATCH,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()


@tableManager.table
class DuelsView(VirtualTable):

    def __init__(self):
        pass

    @computed(paginate=True)
    def game_ids(self) -> List[int]:
        return Game.objects.filter(mode=Game.Mode.DUELS).exclude(status=Game.Status.FINISHED).values_list('id', flat=True)

    @computed
    def online_player_count(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.DUELS,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()


@tableManager.table
class GameModeStatsView(VirtualTable):

    def __init__(self):
        pass

    @computed
    def ranked_online(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.RANKED,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()

    @computed
    def pubs_online(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.PUB,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()

    @computed
    def duels_online(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.DUELS,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()

    @computed
    def deathmatch_online(self) -> int:
        return PlayerSession.objects.filter(
            game__mode=Game.Mode.DEATHMATCH,
            status=PlayerSession.Status.PARTICIPATING,
            state=PlayerSession.State.IN_GAME
        ).count()

    @computed
    def ranked_games(self) -> int:
        return Game.objects.filter(mode=Game.Mode.RANKED).exclude(status=Game.Status.FINISHED).count()

    @computed
    def pubs_games(self) -> int:
        return Game.objects.filter(mode=Game.Mode.PUB).exclude(status=Game.Status.FINISHED).count()

    @computed
    def duels_games(self) -> int:
        return Game.objects.filter(mode=Game.Mode.DUELS).exclude(status=Game.Status.FINISHED).count()

    @computed
    def deathmatch_games(self) -> int:
        return Game.objects.filter(mode=Game.Mode.DEATHMATCH).exclude(status=Game.Status.FINISHED).count()


@tableManager.table
class RankedView(VirtualTable):

    def __init__(self):
        pass

    @computed
    def my_queue_id(self) -> Optional[int]:
        if not self.context['player']:
            return None

        queue = PlayerQueue.players.through.objects.filter(player_id=self.context['player'].id).first()
        if queue:
            return queue.playerqueue.id

    @computed(paginate=True)
    def queue_ids(self) -> List[int]:
        return PlayerQueue.objects.filter(type=PlayerQueue.Type.RANKED).values_list('id', flat=True)


@tableManager.table
class PlayerQueueTable(Table[PlayerQueue]):
    type: int
    locked: bool
    confirmed: bool
    match_id: int
    captain_a_id: int
    captain_b_id: int

    @computed(paginate=True)
    def team_a(self) -> List[int]:
        return self.team_a.values_list('id', flat=True)

    @computed(paginate=True)
    def team_b(self) -> List[int]:
        return self.team_b.values_list('id', flat=True)

    @computed(paginate=True)
    def player_ids(self) -> List[int]:
        return self.players.values_list('id', flat=True)

    @computed
    def confirmed_count(self) -> int:
        return self.confirmed_players.count()

    @computed
    def confirmed_by_me(self) -> bool:
        if not self.context['player']:
            return False

        return self.confirmed_players.filter(id=self.context['player'].id).exists()


type_defs = """
    type Query {
        player_ids: [Int],
        team_ids: [Int],
        event_ids: [Int],
        game_ids: [Int],
        match_ids: [Int],
        
        server(id: Int): Server
""" + tableManager.get_graphql_requests() + """
    }
    
    type Server {
        game_ids: [Int]
        games: [Game]
        id: Int
    }

""" + tableManager.get_graphql_responses() + """
    
"""

query = QueryType()

print(type_defs)

tableManager.define_resolvers(query)


@query.field("player")
def resolve_player(_, info, id):
    player = Player.objects.get(id=id)
    owned_team = Team.objects.filter(owner=player).first()
    if owned_team:
        player.owned_team_id = owned_team.id
    else:
        player.owned_team_id = None

    return player


@query.field("event")
def resolve_event(_, info, id):
    return Event.objects.get(id=id)


@query.field("player_ids")
def resolve_player(_, info):
    return [x.id for x in Player.objects.all()]


@query.field("team_ids")
def resolve_team(_, info):
    return [x.id for x in Team.objects.all()]


@query.field("event_ids")
def resolve_event(_, info):
    return [x.id for x in Event.objects.all()]


@query.field("game_ids")
def resolve_game(_, info):
    return [x.id for x in Game.objects.all()]


@query.field("match_ids")
def resolve_match(_, info):
    return [x.id for x in Match.objects.all()]


@query.field("server")
def resolve_team(_, info, id):
    return {}


server = ObjectType("Server")


@server.field("id")
def resolve_server_id(obj, info):
    return 1


@server.field("games")
def resolve_lobbies(obj, info):
    return Game.objects.exclude(status=Game.Status.FINISHED)


@server.field("game_ids")
def resolve_lobbies_ids(obj, info):
    return [x.id for x in Game.objects.exclude(status=Game.Status.FINISHED)]


# Create executable schema instance
schema = make_executable_schema(
    type_defs, query, server, *tableManager.get_gql_objects()
)
