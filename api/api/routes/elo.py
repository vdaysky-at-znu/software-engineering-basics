from fastapi import APIRouter

from api.models import Game
from api.services.ranked import compute_elo

router = APIRouter()


@router.get("/predict/{game_id}")
def get_elo(game_id: int):

    game = Game.objects.get(id=game_id)

    a_win, a_loose = compute_elo(game.team_a, game.team_b)
    b_win, b_loose = compute_elo(game.team_b, game.team_a)

    return {
        "team_a_win": a_win,
        "team_a_loss": a_loose,
        "team_b_win": b_win,
        "team_b_loss": b_loose,
    }
