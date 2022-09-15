from typing import Optional

from pydantic import BaseModel

from api.dependencies import PlayerField, GameField, InGameTeamField


class ServerStartEvent(BaseModel):
    pass


class RequestCreateGameEvent(BaseModel):
    mapName: str
    plugins: list


class RequestPlayerJoinGameEvent(BaseModel):
    game: GameField
    player: PlayerField


class PlayerLeaveGameEvent(BaseModel):
    game: GameField
    player: PlayerField


class RequestPlayerTeamChangeEvent(BaseModel):
    game: GameField
    player: PlayerField
    team: str


class PreGameEndEvent(BaseModel):
    game: GameField
    winner: Optional[InGameTeamField]
    looser: Optional[InGameTeamField]


class GameStartedEvent(BaseModel):
    game: GameField

