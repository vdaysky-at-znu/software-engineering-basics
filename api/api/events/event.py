import random

from pydantic import BaseModel


class EventOut:
    """ Event that will be sent via websocket to frontend. Usually represents change in the database """

    def __init__(self, type, payload=None, message=None, status=200, session_key=None):
        self.type = type
        self.payload = payload
        self.message = message
        self.status = status
        self.session_key = session_key
        self.message_id = random.randint(0, 1_000_000)

    def dict(self):
        return {
            'type': self.type,
            'payload': self.payload,
            'message': self.message,
            'status': self.status,
            'session_key': self.session_key,
            'message_id': self.message_id
        }

    def __str__(self):
        return f"EventOut[{self.status}]<{self.type}>"

    class Type:
        """ Event types to send. Websocket should ideally be used only to send events.
        Everything else should be done via HTTP. """

        # internal workings
        MODEL_UPDATE = "ModelUpdateEvent"
        MODEL_CREATE = "ModelCreateEvent"


class AbsEvent(BaseModel):
    """
        Event from Frontend/Bukkit that has abstract payload.
        It could be received from either websocket or HTTP.
        it will be decoded based on name of the event type
        into new instance.
    """

    name: str  # Event name, corresponds to bukkit event name
    payload: dict  # All the fields for that event
