from fastapi import APIRouter

from api.routes import roster, player, auth, event, match, game, bukkit, elo


def get_v1_router():
    v1_router = APIRouter()

    v1_router.include_router(prefix="/roster", router=roster.router)
    v1_router.include_router(prefix="/player", router=player.router)
    v1_router.include_router(prefix="/auth", router=auth.router)
    v1_router.include_router(prefix="/event", router=event.router)
    v1_router.include_router(prefix="/match", router=match.router)
    v1_router.include_router(prefix="/game", router=game.router)
    v1_router.include_router(prefix="/bukkit", router=bukkit.router)
    v1_router.include_router(prefix="/elo", router=elo.router)
    return v1_router

