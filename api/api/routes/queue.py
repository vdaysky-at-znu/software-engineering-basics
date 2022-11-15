from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency
from api.models import PlayerQueue, Player
from api.schemas.queue import Queue, PickPlayer
from api.services.queue import join_queue, leave_queue, confirm_queue, pick_player

router = APIRouter()


@router.post("/join")
async def join(data: Queue, player: Player = PlayerAuthDependency):

    return await join_queue(player, data.queue)


@router.post("/leave")
async def leave(data: Queue, player: Player = PlayerAuthDependency):

    return await leave_queue(player, data.queue)


@router.post("/confirm")
async def confirm(data: Queue, player: Player = PlayerAuthDependency):

    return await confirm_queue(player, data.queue)


@router.post("/pick")
async def pick(data: PickPlayer, player: Player = PlayerAuthDependency):

    return await pick_player(player, data.player, data.queue)

