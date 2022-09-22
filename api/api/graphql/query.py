import inspect
import json
from typing import List

from ariadne import QueryType, make_executable_schema, ObjectType

from api.graphql.virtual import TableManager, VirtualTable, Table, computed
from api.models import Player, Team, Role, PlayerPermission, Game, InGameTeam, PlayerSession, Event, Match, Invite, \
    MapPickProcess, MapPick

tableManager = TableManager()


@tableManager.table
class EventTable(Table[Event]):
    id: int
    name: str
    start_date: str

    @computed
    def match_ids(self) -> List[int]:
        return [match.id for match in self.matches.all()]


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
    def permission_ids(self) -> List[int]:
        return [perm.id for perm in self.permissions.all()]


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
    def member_ids(self) -> List[int]:
        return [p.id for p in Player.objects.filter(team_id=self.id)]


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
    finished: bool
    started: bool
    match_id: int
    team_a_id: int
    team_b_id: int
    config: Config
    plugins: List[str]

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
    def map_ids(self) -> List[int]:
        return [m.id for m in self.maps.all()]


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

    @computed
    def player_ids(self) -> List[int]:
        return [p.id for p in self.players.all()]


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
    def player_ids(self) -> List[FftPlayerId]:
        return [
            FftPlayerId(player_id=player.id, team_id=self.team_id)
            for player in Player.objects.filter(team=None)
        ]

    def __init__(self, team_id: int):
        self.team_id = team_id


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
    
    type Hub {
        id: Int
        world: String
        players: [Player]
        player_ids: [Int]
    }
    
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
