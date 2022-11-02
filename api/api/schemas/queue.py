from pydantic import BaseModel

from api.dependencies import QueueField, PlayerField


class Queue(BaseModel):
    queue: QueueField


class PickPlayer(BaseModel):
    queue: QueueField
    player: PlayerField

