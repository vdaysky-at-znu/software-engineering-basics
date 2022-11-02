import asyncio
import traceback
from collections import defaultdict
from typing import Type, Any

from pydantic import BaseModel

from api.events.event import AbsEvent


class WaitObject:

    def __init__(self, registerer):
        self.registerer = registerer

    def on(self, model) -> asyncio.Future:
        return self.registerer(model, 'on')

    def pre(self, model) -> asyncio.Future:
        return self.registerer(model, 'pre')

    def post(self, model) -> asyncio.Future:
        return self.registerer(model, 'post')


class EventManager:

    def __init__(self):
        self.handlers = defaultdict(list)
        self.waiters = []

    def _execute_waiters(self, event, model, waiter_type):
        waiters_to_remove = []
        for waiter in self.waiters:
            _waited_event, _model, _waiter_type, _future = waiter

            if model != _model:
                continue

            if waiter_type != waiter_type:
                continue

            if not event == _waited_event and (isinstance(_waited_event, type) and not isinstance(event, _waited_event)):
                continue

            waiters_to_remove.append(waiter)
            _future.set_result(event)

        for waiter in waiters_to_remove:
            self.waiters.remove(waiter)

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

    async def propagate_event(self, sender: Any, event: BaseModel):
        """
            Propagate arbitrary pydantic schema as event
        """
        abs_event = AbsEvent(name=type(event).__name__, payload=event.dict())
        return await self.propagate_abstract_event(abs_event, sender)

    async def propagate_abstract_event(self, event: AbsEvent, entity):
        """
            Propagate generic event with strict schema
        """

        print(f"Propagate event {event.name}")

        response = None

        self._execute_waiters(event, entity, 'pre')
        self._execute_waiters(event, entity, 'on')

        for handler in self.handlers[event.name]:
            try:
                response = handler(entity, event.payload)
                if asyncio.iscoroutine(response):
                    response = await response
            except Exception:
                traceback.print_exc()

        self._execute_waiters(event, entity, 'post')

        return response

    def wait(self, event: Type[BaseModel], timeout=None) -> WaitObject:

        async def fail_task_if_did_not_succeed(future: asyncio.Future):
            await asyncio.sleep(timeout)
            if not future.done():
                future.set_exception(TimeoutError(f'Event Waiter timed out after {timeout} seconds'))

        def register_waiter(model, waiter_type):
            future = asyncio.Future()

            if timeout:
                asyncio.create_task(fail_task_if_did_not_succeed(future))

            self.waiters.append((event, model, waiter_type, future))
            return future

        return WaitObject(register_waiter)
