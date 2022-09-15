import asyncio
import random
from uuid import UUID

from fastapi import APIRouter

from api.dependencies import PlayerDependency, PlayerAuthDependency, InviteDependency
from api.exceptions import BadRequestError, PermissionError
from api.models import Player, Invite, Role
from api.adapters.mojang import get_last_name

router = APIRouter()


# @router.get("/{player}", response_model=PlayerData)
# def get_player(player: Player = PlayerDependency()):
#     return player

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


@router.get('/fft')
def get_fft():
    fft_players = Player.objects.filter(team=None)
    return fft_players


@router.post('/{player}/invite')
def invite_player(player: Player = PlayerDependency(True), inviter: Player = PlayerAuthDependency):

    team = inviter.team

    if team is None:
        raise BadRequestError('Not in team')

    if not inviter.has_perm('api.team_owner') and not inviter.has_perm('api.team_leader'):
        return PermissionError

    invite = Invite.objects.get_or_create(player=player, team=team)
    # todo broadcast to invited player
    return invite

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
