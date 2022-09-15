from pydantic.main import BaseModel

from api.constants import LocationCode


class CreateTeam(BaseModel):
    short_name: str
    name: str
    location: LocationCode
