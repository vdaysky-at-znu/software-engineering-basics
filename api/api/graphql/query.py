import inspect
import json
from typing import List, TypeVar, Generic, get_args, Type

from ariadne import QueryType, make_executable_schema, ObjectType
from django.db.models import Q, Sum, Count

from api.graphql.virtual import TableManager, VirtualTable, Table, computed, PaginatedTable, VirtualGenericTable
from api.models import Player, Team, Role, PlayerPermission, Game, InGameTeam, PlayerSession, Event, Match, Invite, \
    MapPickProcess, MapPick, GamePlayerEvent

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
    def permission_ids(self, page: int = 0, size: int = 10) -> Page[int]:
        return Page(self.permissions.count(), self.permissions.values_list('id', flat=True)[page * size:page * size + size])


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


@tableManager.table(queryable=False)
class Config(VirtualTable):
    overrides: str

    def __init__(self, game_id: int):
        self.overrides = json.dumps({
            "something": 1
        })


@tableManager.table
class GameTable(Table[Game]):
    id: int
    map: str
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
    def blacklist(self) -> List[int]:
        return []


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

    @computed(paginate=True)
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

        stats = GamePlayerEvent.objects.all()

        print(f"get stats")
        if self.player_id:
            print(f"with player: {self.player_id}")
            stats = stats.filter(player_id=self.player_id)

        if self.in_game_team_id:
            print(f"with team: {self.in_game_team_id}")
            team = InGameTeam.objects.get(id=self.in_game_team_id)
            self.game_id = team.game.id
            stats = stats.filter(game=team.game, player_id__in=team.sessions.values_list('player', flat=True))

        if self.game_id:
            print(f"with game: {self.game_id}")
            stats = stats.filter(game_id=self.game_id)

        # find all players with stats
        players = stats.values_list('player_id', flat=True).distinct()
        print(f"Players: {players}")

        return [PlayerStatId(player, self.game_id) for player in players]


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
    return Game.objects.filter(finished=False)


@server.field("game_ids")
def resolve_lobbies_ids(obj, info):
    return [x.id for x in Game.objects.filter(finished=False)]


# Create executable schema instance
schema = make_executable_schema(
    type_defs, query, server, *tableManager.get_gql_objects()
)
