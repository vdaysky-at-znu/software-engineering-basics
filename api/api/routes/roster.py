import random
import string

from django.contrib.auth.models import Permission
from django.db.models import Q
from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency
from api.models import Team, Player
from api.util import response
from api.schemas.team import CreateTeam

router = APIRouter()


# @router.get("/{roster}")
# def get_roster(roster: Team = RosterDependency()):
#     return roster

@router.get("/t-create")
async def test_events():
    # create a team with randomly generated name
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    random_short_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    team = Team.objects.create(
        short_name=random_short_name,
        full_name=random_name,
        owner=Player.objects.first()
    )


@router.get("/t-update/{id}")
async def test_events(id: int):
    # create a team with randomly generated name
    team = Team.objects.get(id=id)
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    team.full_name = random_name
    team.save()


@router.get('/name/{name}/status')
def check_team_name(name: str):
    exists = Team.objects.filter(Q(short_name=name) | Q(full_name=name)).exists()
    return response(data={'available': {exists}})


@router.post('/create')
async def register_team(roster: CreateTeam, player: Player = PlayerAuthDependency):

    if player.team is not None and not player.is_superuser:
        return "already in team"

    if not player.has_perm('api.can_create_teams'):
        return "no perm"

    if Team.objects.filter(Q(short_name=roster.name) | Q(full_name=roster.short_name)).exists():
        return "existing name"

    team = Team.objects.create(
        short_name=roster.short_name,
        full_name=roster.name,
        location=roster.location,
        owner=player
    )

    # todo trigger 'team registered' packet (from signals would be nice)
    # todo trigger 'player join team'

    # update user's perms to team leader
    team_leader_perm = Permission.objects.get(codename="team_owner")
    player.user_permissions.add(team_leader_perm)
    player.team = team
    player.save()

# send update to user
#  TODO: use signals, broadcast to every subscriber
#   here's a nice thought: when some component that requires list of users renders
#   I use hook to subscribe to update events. When component is destroyed, I unsubscribe.
#   so this line should be removed in close future
# await packet.initiator.send_packet(PacketType.USER_DATA, packet.user)

