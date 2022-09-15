from pydantic.main import BaseModel

from api.constants import GameMap
from api.dependencies import MatchField


class CreateGame(BaseModel):
    match: MatchField
    map: GameMap

