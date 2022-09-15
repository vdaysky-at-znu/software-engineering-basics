from fastapi import APIRouter

from api.events.bukkit import BukkitEventManager
from api.events.event import AbsEvent
from api.models import AuthSession, Player
from api.services.minestrike import MineStrike

router = APIRouter()


@router.post('/event')
async def post_event(event: AbsEvent):
    response = await BukkitEventManager.propagate_event(event, MineStrike(1))

    return {
        "response": response
    }
