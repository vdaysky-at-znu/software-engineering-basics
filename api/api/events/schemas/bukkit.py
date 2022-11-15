from typing import Optional

from pydantic import BaseModel

from api.dependencies import PlayerField, GameField, InGameTeamField


class IntentEvent(BaseModel):
    pass


class ServerStartEvent(BaseModel):
    pass


class CreateGameIntentEvent(IntentEvent):
    mapName: str
    mode: str
    player: PlayerField


class PlayerJoinGameIntentEvent(IntentEvent):
    game: GameField
    player: PlayerField


class PlayerLeaveGameEvent(BaseModel):
    game: GameField
    player: PlayerField


class PlayerTeamChangeIntentEvent(IntentEvent):
    game: GameField
    player: PlayerField
    team: str


class PreGameEndEvent(BaseModel):
    game: GameField
    winner: Optional[InGameTeamField]
    looser: Optional[InGameTeamField]


class GameStartedEvent(BaseModel):
    game: GameField


class PlayerJoinServerEvent(BaseModel):
    player: PlayerField


class PlayerLeaveServerEvent(BaseModel):
    player: PlayerField

