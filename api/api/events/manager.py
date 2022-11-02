import asyncio
import traceback
from collections import defaultdict
from typing import Type

from pydantic import BaseModel

from api.events.event import AbsEvent


class EventManager:

    def __init__(self):
        self.handlers = defaultdict(list)

    def on(self, event: Type[BaseModel]):
        def inner(func):
            print(f"Registered handler {func.__name__} for event {event}")

            if isinstance(event, str):
                self.handlers[event].append(func)
            else:
                self.handlers[event.__name__].append(
                    lambda sender, evt_payload:
                    func(
                        sender,
                        event.parse_obj(evt_payload)
                    )
                )

        return inner

    async def propagate_event(self, event: AbsEvent, entity):
        print(f"Propagate event {event.name}")
        response = None
        for handler in self.handlers[event.name]:
            try:
                response = handler(entity, event.payload)
                if asyncio.iscoroutine(response):
                    response = await response
            except Exception:
                traceback.print_exc()

        return response
