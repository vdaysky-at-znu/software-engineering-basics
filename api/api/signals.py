import asyncio

from asgiref.sync import sync_to_async, async_to_sync
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from api.models import Event, Match, Game, Player, Team, MapPick, MapPickProcess, PlayerQueue, MatchTeam, InGameTeam

from django.db.models.signals import m2m_changed


def m2m_change_hook(sender, action, instance, **kwargs):
    table_changed(False, False, instance)


def register_sync_var(model):

    receiver(post_save, sender=model)(
        lambda sender, instance, created, **kwargs: table_changed(created, False, instance)
    )
    receiver(pre_delete, sender=model)(
        lambda sender, instance, **kwargs: table_changed(False, True, instance)
    )


def table_changed(created, deleted, instance):
    """ Send events to all subscribed websockets """

    from api.consumers import WsPool

    event = "create" if created else ('delete' if deleted else 'update')
    print(f"send event: {event} on  {instance}")
    asyncio.create_task(WsPool.model_event(event=event, instance=instance))


synced_models = {
    Match,
    Game,
    Event,
    Player,
    Team,
    MapPick,
    MapPickProcess,
}

synced_m2m = {
    PlayerQueue.players.through,
    PlayerQueue.confirmed_players.through,
    MatchTeam.players.through,
}


def register_signals():
    for model in synced_models:
        register_sync_var(model)

    for model in synced_m2m:
        print(f"Register signal for {model}")
        m2m_changed.connect(m2m_change_hook, sender=model)

