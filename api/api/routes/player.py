import asyncio
import random
import string
import uuid

from django.db.models import Q
from fastapi import APIRouter
from uuid import UUID

from api.dependencies import PlayerDependency, PlayerAuthDependency, InviteDependency
from api.exceptions import BadRequestError, PermissionError
from api.models import Player, Invite, Role
from api.adapters.mojang import get_last_name
from api.schemas.player import SendInviteData

router = APIRouter()


@router.get("/testcreate")
async def test_create():

    for _ in range(100):
        name = ''.join(random.choices(string.ascii_lowercase, k=10))
        uid = uuid.uuid4()

        player = Player.objects.create_user(
            username=name,
            uuid=uid,
            password="1",
            role=Role.objects.get(name="default")
        )
        print(player)


@router.get("/t-update/{player}")
async def get_player(player: int):
    player = Player.objects.get(id=player)
    # generate random name from characters
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    player.username = name
    player.save()
    return player


@router.get("/id/{uuid}")
async def get_player_id(uuid: UUID):
    player = Player.objects.filter(uuid=uuid)

    role = Role.objects.get(name="default")

    if not player.exists():
        return Player.objects.create(
            uuid=uuid,
            team=None,
            role=role,
            username=await get_last_name(uuid) or "".join([random.choice(list("qwertyuiopasdfghjkklzxcvbnm")) for _ in range(10)]),
            password=""
        ).id
    return player.get().id


@router.get("/elo-increment")
async def increment():
    p = Player.objects.get(uuid="2837311f-ac3a-405c-9a28-1defb3cf9065")
    for x in range(10):
        print(f"increment")
        await asyncio.sleep(5)
        p.elo += 1
        p.save()
    return {'uuid': p.uuid, 'elo': p.elo}


@router.get("/{uuid}/name")
async def get_player(uuid: UUID):
    return await get_last_name(uuid)


@router.get("/find/{query}")
def find_player(query: str):
    player = Player.objects.filter(Q(username__iexact=query) | Q(uuid__iexact=query)).first()

    player_id = player.id if player else None

    return {
        'player_id': player_id,
    }


@router.get('/fft')
def get_fft():
    fft_players = Player.objects.filter(team=None)
    return [player.id for player in fft_players]


@router.post('/invite')
def invite_player(data: SendInviteData, inviter: Player = PlayerAuthDependency):

    team = inviter.team
    player = Player.objects.get(id=data.player_id)

    is_owner = False
    if team is None:
        owned_team = inviter.get_owned_team()
        if owned_team:
            team = owned_team
            is_owner = True
        else:
            raise BadRequestError("You are not in a team")

    if not is_owner and not inviter.has_perm('api.team_leader'):
        raise PermissionError("You are not allowed to invite players")

    invite, created = Invite.objects.get_or_create(player=player, team=team)
    # todo broadcast to invited player
    return invite.id

#
# @router.get('/invites')
# def get_invites(player: Player = PlayerAuthDependency):
#     return player.invites.all()


@router.post('/invite/{invite}/accept')
def accept_invite(player: Player = PlayerAuthDependency, invite: Invite = InviteDependency):
    if invite.player != player:
        raise BadRequestError

    if invite.status is not None:
        raise BadRequestError

    # todo: much more handling needed imo
    #  player has to leave old team properly
    player.team = invite.team
    player.save()

    invite.accepted = True
    invite.save()

    return player


@router.post('/invite/{invite}/decline')
def decline_invite(player: Player = PlayerAuthDependency, invite: Invite = InviteDependency):
    if invite.player != player:
        raise BadRequestError

    if invite.status is not None:
        raise BadRequestError

    invite.declined = True
    invite.save()

    return player


@router.get("/uuid")
async def get_uuid(name: str):
    return await get_uuid(name)


# @router.post("/create")
# def create_player(player: PlayerCreate):
#     if Player.objects.filter(uuid=player.uuid).exists():
#         raise HTTPException(400, "Player already exists")
#
#     player = Player.objects.create(
#         uuid=player.uuid,
#         location_code=player.location_code.value
#     )
#
#     return player


codes = {}


# @router.post("/{player}/code/generate")
# def generate_code(player: Player = PlayerDependency()):
#     player_name = player.username
#
#     if codes.get(player_name):
#         code = codes.get(player_name)
#         print(f"got saved code for '{player_name}': '{code}'")
#     else:
#         code = random.randrange(100_000, 999_999)
#         codes[player_name] = code
#         print(f"generated code for '{player_name}': '{code}'")
#
#     return True


# @router.post("/{player}/code/verify")
# def verify_player(data: VerifyPlayer, player: Player = PlayerDependency()):
#
#     if player.verified:
#         raise HTTPException(400, "Already verified")
#
#     if data.verification_code:
#         player.verify()
#
#     return player
