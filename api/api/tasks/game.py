from api.constants import AVAILABLE_PUBS_THRESHOLD
from api.models import Game
from api.services.game import create_pub, create_deathmatch, create_duels


async def keep_open_pubs():
    """ Make sure there are always some open pubs. """

    open_pubs = Game.objects.filter(
        mode=Game.Mode.PUB,
        status=Game.Status.NOT_STARTED,
    ).count()

    for _ in range(AVAILABLE_PUBS_THRESHOLD - open_pubs):
        # create new game
        await create_pub()


async def keep_open_deathmatch():
    """ Make sure there are always some open deathmatch. """

    open_deathmatch = Game.objects.filter(
        mode=Game.Mode.DEATHMATCH,
        status=Game.Status.NOT_STARTED,
    ).count()

    for _ in range(AVAILABLE_PUBS_THRESHOLD - open_deathmatch):
        # create new game
        await create_deathmatch()


async def keep_open_duels():
    """ Make sure there are always some open duels. """

    open_duels = Game.objects.filter(
        mode=Game.Mode.DUELS,
        status=Game.Status.NOT_STARTED,
    ).count()

    for _ in range(AVAILABLE_PUBS_THRESHOLD - open_duels):
        # create new game
        await create_duels()
