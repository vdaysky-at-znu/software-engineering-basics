from pydantic import BaseModel


class BukkitInitEvent(BaseModel):
    secret: str


class PingEvent(BaseModel):
    ping_id: int


class ConfirmEvent(BaseModel):
    confirm_message_id: int
