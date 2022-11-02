from typing import Any

from pydantic import BaseModel


class PlayerLeftGame(BaseModel):
    session: Any


class PlayerRosterChange(BaseModel):
    session: Any
    old_roster: Any
    new_roster: Any


class PlayerStatusChange(BaseModel):
    session: Any
    old_status: int
    new_status: int


class PlayerJoinGame(BaseModel):
    session: Any


