from pydantic.main import BaseModel

from api.constants import GameMap
from api.dependencies import MatchField, GameField


class CreateGame(BaseModel):
    match: MatchField
    map: GameMap


class JoinGame(BaseModel):
    game: GameField
