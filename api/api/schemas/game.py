from pydantic.main import BaseModel

from api.dependencies import MatchField, GameField, MapField


class CreateGame(BaseModel):
    match: MatchField
    map: MapField


class JoinGame(BaseModel):
    game: GameField
