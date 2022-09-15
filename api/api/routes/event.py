from datetime import datetime

from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency
from api.models import Player, Event
from api.schemas.event import CreateEvent
from api.exceptions import PermissionError, BadRequestError
router = APIRouter()


@router.post('/create')
def create_event(data: CreateEvent, player: Player = PlayerAuthDependency):
    if not player.has_perm("api.can_create_events"):
        raise PermissionError

    if len(data.name) < 5:
        raise BadRequestError('Name too short')

    if data.start_date < datetime.now():
        raise BadRequestError('Date is in the past')

    return Event.objects.create(name=data.name, start_date=data.start_date)
