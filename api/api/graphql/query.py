import json
from typing import List

from ariadne import QueryType, make_executable_schema, ObjectType

from api.graphql.virtual import VirtualTableManager, VirtualTable
from api.models import Player, Team, Role, PlayerPermission, Game, InGameTeam, PlayerSession, Event, Match, Invite

virtualTableManger = VirtualTableManager()


@virtualTableManger.table(queryable=True)
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


@virtualTableManger.table
class FftPlayerId(VirtualTable):
    player_id: int
    team_id: int

    def __init__(self, player_id: int, team_id: int):
        self.player_id = player_id
        self.team_id = team_id


@virtualTableManger.table
class FftPlayerView(VirtualTable):
    player_ids: List[FftPlayerId]

    def __init__(self, team_id: int):
        self.player_ids = [
            FftPlayerId(player_id=player.id, team_id=team_id)
            for player in Player.objects.filter(team=None)
        ]


type_defs = """
    type Query {
        player_ids: [Int],
        team_ids: [Int],
        event_ids: [Int],
        game_ids: [Int],
        match_ids: [Int],
        
        player(id: Int): Player
        team(id: Int!): Team
        role(id: Int!): Role
        permission(id: Int): Permission
        server(id: Int): Server
        game(id: Int): Game
        inGameTeam(id: Int): InGameTeam
        playerSession(id: Int): PlayerSession
        """ + virtualTableManger.get_graphql_requests() + """
    }
    
    type Server {
        game_ids: [Int]
        games: [Game]
        id: Int
    }
    
    """ + virtualTableManger.get_graphql_responses() + """
    
    type Game {
        id: Int
        map: String
        finished: Boolean
        started: Boolean
        match: Match
        team_a: InGameTeam
        team_b: InGameTeam
        team_a_id: Int
        team_b_id: Int
        session_ids: [Int]
        config: Config
        blacklist: [Int]
        plugins: [String] 
    }
    
    type PlayerSession {
        id: Int
        player_id: Int
        game_id: Int
        roster_id: Int
    }
    
    type Config {
        overrides: String
    }
    
    type Match {
        id: Int
        team_one: Team
        team_one_id: Int
        team_two: Team
        team_two_id: Int
        name: String
        start_date: String
        actual_start_date: String
        actual_end_date: String
        event: Event
        map_count: Int
        map_pick_process: MapPickProcess
        map_pick_process_id: Int
    }
    
    type MapPickProcess { 
        id: Int
        finished: Boolean
        next_action: Int
        turn: Team
        maps: [MapPick]
        map_ids: [Int]
    }
    
    type MapPick {
        id: Int
        map_name: String
        selected_by: Team
        picked: Boolean
        process: MapPickProcess
        process_id: Int
    }
    
    type Event {
        id: Int
        name: String
        start_date: String
        matches: [Match]
        match_ids: [Int]
    }
    
    type InGameTeam {
        id: Int
        name: String
        starts_as_ct: Boolean
        players: [Player]
        player_ids: [Int]
    }
    
    type Hub {
        id: Int
        world: String
        players: [Player]
        player_ids: [Int]
    }

    type Player {
        id: Int!
        uuid: String!
        username: String!
        elo: Int!
        role_id: Int!
        role: Role
        team: Team
        team_id: Int 
        owned_team_id: Int
    }
    
    type Role {
        id: Int!
        name: String!
        tab_prefix: String!
        tab_color: String!
        chat_prefix: String!
        chat_suffix: String!
        chat_color: String!
        chat_message_color: String!
        team_override_color: Boolean!
        
        permission_ids: [Int]
        permissions: [Permission]
    }
    
    type Permission {
        id: Int!
        name: String!
    }
    
    type Team {
        id: Int
        short_name: String
        full_name: String
        location_code: String
        members: [Player]
        member_ids: [Int]
    }
    
"""

query = QueryType()

virtualTableManger.define_resolvers(query)


@query.field("player")
def resolve_player(_, info, id):
    player = Player.objects.get(id=id)
    owned_team = Team.objects.filter(owner=player).first()
    if owned_team:
        player.owned_team_id = owned_team.id
    else:
        player.owned_team_id = None

    return player


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


@query.field("team")
def resolve_team(_, info, id):
    return Team.objects.get(id=id)


@query.field("game")
def resolve_team(_, info, id):
    return Game.objects.get(id=id)


@query.field("server")
def resolve_team(_, info, id):
    return {}


@query.field("role")
def resolve_role(_, info, id):
    return Role.objects.get(id=id)


@query.field("inGameTeam")
def resolve_role(_, info, id):
    return InGameTeam.objects.get(id=id)


@query.field("permission")
def resolve_permission(_, info, id):
    return PlayerPermission.objects.get(id=id)


@query.field("playerSession")
def resolve_session(_, info, id):
    return PlayerSession.objects.get(id=id)


player = ObjectType("Player")
server = ObjectType("Server")
role = ObjectType("Role")
permission = ObjectType("Permission")
team = ObjectType("Team")
in_game_team = ObjectType("InGameTeam")
match = ObjectType("Match")
game = ObjectType("Game")
event = ObjectType("Event")
map_pick = ObjectType("MapPick")
map_pick_process = ObjectType("MapPickProcess")
player_session = ObjectType("PlayerSession")


@server.field("id")
def resolve_server_id(obj, info):
    return 1


@server.field("games")
def resolve_lobbies(obj, info):
    return Game.objects.filter(finished=False)


@server.field("game_ids")
def resolve_lobbies_ids(obj, info):
    return [x.id for x in Game.objects.filter(finished=False)]


@game.field("config")
def resolve_game_config_overrides(obj, info):

    config = json.dumps({
        "randomthing": 1
    })

    return {
        "overrides": config
    }


@game.field("blacklist")
def resolve_game_blacklist(obj, info):
    return []


@game.field("session_ids")
def resolve_session_ids(obj, info):
    return [x.id for x in obj.sessions.all()]


@role.field("permission_ids")
def resolve_permission_ids(obj, info):
    return [x.id for x in obj.permissions.all()]


@role.field("permissions")
def resolve_permission_ids(obj, info):
    return obj.permissions.all()


@team.field("members")
def resolve_team_members(obj, *x):
    return obj.players.all()


@team.field("member_ids")
def resolve_team_member_ids(obj, *x):
    return [x.id for x in obj.players.all()]


@in_game_team.field("players")
def resolve_ig_team_players(obj, *x):
    return [x.player for x in obj.sessions.all()]


@in_game_team.field("player_ids")
def resolve_ig_team_players(obj, *x):
    return [x.player.id for x in obj.sessions.all()]


# Create executable schema instance
schema = make_executable_schema(
    type_defs,
    query, player, role, team,
    map_pick, map_pick_process,
    event, match, in_game_team,
    game, server, player_session
)
