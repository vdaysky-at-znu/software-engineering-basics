from datetime import datetime

from pydantic.class_validators import validator
from pydantic.main import BaseModel

from api.constants import GameMap
from api.dependencies import EventField, TeamField


class CreateMatch(BaseModel):
    event: EventField
    start_date: datetime
    name: str
    team_a: TeamField
    team_b: TeamField
    map_count: int

    @validator('map_count')
    def validate_map_count(cls, v):
        assert v in [1, 3, 5], 'Invalid map count'
        return v


class PickMap(BaseModel):
    map: GameMap
    is_picked: bool
