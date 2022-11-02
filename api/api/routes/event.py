import random
import string
from datetime import datetime

from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency
from api.models import Player, Event
from api.schemas.event import CreateEvent
from api.exceptions import PermissionError, BadRequestError

import pytz

router = APIRouter()


@router.get("/test")
async def test():
    # generate random combination of characters
    name = "".join(random.choices(string.ascii_letters + string.digits, k=10))

    Event.objects.create(
        name=name,
        start_date=datetime.now(pytz.utc),
    )


@router.post('/create')
async def create_event(data: CreateEvent, player: Player = PlayerAuthDependency):
    if not player.has_perm("api.can_create_events"):
        raise PermissionError("You don't have permission to create events")

    if len(data.name) < 5:
        raise BadRequestError('Name too short')

    if data.start_date < datetime.now(tz=pytz.UTC):
        raise BadRequestError('Date is in the past')

    evt = Event.objects.create(name=data.name, start_date=data.start_date)

    return evt.id
