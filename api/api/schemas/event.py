from datetime import datetime

from pydantic.main import BaseModel


class CreateEvent(BaseModel):
    start_date: datetime
    name: str
