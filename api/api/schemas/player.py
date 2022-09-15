from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from api.constants import LocationCode
from djantic import ModelSchema

from api.models import Player, Team, PlayerPermission, Role


class PlayerCreate(BaseModel):
    uuid: UUID
    location_code: LocationCode


class PlayerBrief(ModelSchema):
    class Config:
        model = Player
        include = ['uuid', 'elo']


class PermissionData(ModelSchema):

    class Config:
        model = PlayerPermission
        include = ['name']


class RoleData(ModelSchema):
    permissions: List[PermissionData]

    class Config:
        model = Role
        include = [
            'permissions',
            'name',
            'tab_prefix',
            'tab_color',
            'chat_prefix',
            'chat_suffix',
            'chat_color',
            'chat_message_color',
            'team_override_color'
        ]


class PlayerData(ModelSchema):
    team: Optional[TeamData]
    role: Optional[RoleData]

    class Config:
        model = Player
        include = ['uuid', 'elo', 'team', 'role']


class TeamData(ModelSchema):

    class Config:
        model = Team
        include = ['short_name']


PlayerData.update_forward_refs()


class VerifyPlayer(BaseModel):
    verification_code: int = Field(ge=100_000, le=999_999)
