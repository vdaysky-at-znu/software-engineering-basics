from typing import List

from api.models import Player
from api.schemas.permission import PType


def has_permission(player: Player, permission: PType) -> bool:
    if player.role is None:
        return False

    def test_perm(required: List[str], b):
        if not b:
            return False

        present = b.split(".")

        if len(required) < len(present):
            return False

        for i in range(max(len(present), len(required))):
            if len(present) == i + 2:
                return False

            if present[i] != required[i]:
                return present[i] == "*"
        return True

    for perm in player.role.permissions.all():
        if test_perm(permission.path, perm.name):
            return True

    return False

