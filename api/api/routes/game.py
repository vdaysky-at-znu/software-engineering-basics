from fastapi import APIRouter

from api.dependencies import PlayerAuthDependency
from api.models import Player, Match, Game
from api.schemas.game import CreateGame
from api.exceptions import PermissionError, BadRequestError

router = APIRouter()


@router.post('/create')
def create_game(data: CreateGame, player: Player = PlayerAuthDependency):

    if not player.has_perm('api.can_create_game'):
        raise PermissionError

    if len(data.match.games) >= data.match.map_count:
        raise BadRequestError('Match already has all games defined')
    
    return Game.objects.create(match=data.match, map=data.map)
