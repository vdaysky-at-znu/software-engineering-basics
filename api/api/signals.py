import asyncio

from asgiref.sync import sync_to_async, async_to_sync
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from api.models import Event, Match, Game, Player, Team, MapPick, MapPickProcess


def register_sync_var(model):

    receiver(post_save, sender=model)(
        lambda sender, instance, created, **kwargs: table_changed(created, False, instance)
    )
    receiver(pre_delete, sender=model)(
        lambda sender, instance, **kwargs: table_changed(False, True, instance)
    )


def table_changed(created, deleted, instance):
    """ Send events to all subscribed websockets """

    from api.consumers import WsSessionManager

    event = "create" if created else ('delete' if deleted else 'update')
    print(f"send event: {event} on  {instance}")
    asyncio.create_task(WsSessionManager.model_event(event=event, instance=instance))


synced_models = {
    Match,
    Game,
    Event,
    Player,
    Team,
    MapPick,
    MapPickProcess,
}


def register_signals():
    for model in synced_models:
        register_sync_var(model)

