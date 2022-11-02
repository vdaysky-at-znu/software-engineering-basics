from typing import Optional

from django.contrib.auth.hashers import check_password

from api.adapters.mojang import get_uuid
from api.constants import NameStatus
from api.exceptions import BadRequestError
from api.models import Player, AuthSession, Role


async def login_user(username: str, password: str) -> Optional[AuthSession]:

    user = Player.objects.filter(username=username).first()

    # uuid = await get_uuid(username)
    #
    # user = Player.objects.get(uuid=uuid)
    #
    # if not check_password(password, user.password):
    #     return None

    return AuthSession.create(user)

codes = {}


async def register_user(username: str, code: int, password: str) -> AuthSession:
    user_uuid = await get_uuid(username)

    if False and codes.get(username) != code:
        raise ValueError("Invalid Code")

    if Player.objects.filter(uuid=user_uuid).exists():
        raise ValueError("Player already exists")

    role = Role.objects.filter(name="default").first()

    if role is None:
        raise ValueError("No default role")

    player = Player.objects.create_user(
        uuid=user_uuid,
        username=username,
        password=password,
        role=role
    )

    return AuthSession.create(player)


async def get_name_status(name) -> NameStatus:
    uuid = await get_uuid(name)

    if uuid is None:
        return NameStatus.NAME_INVALID

    player = Player.objects.filter(uuid=uuid)

    if player.exists() and player.get().is_verified():
        return NameStatus.NAME_TAKEN

    return NameStatus.NAME_AVAILABLE


def get_player(session_id):
    session = AuthSession.objects.filter(session_key=session_id).first()

    if session is None:
        return None

    return session.player
