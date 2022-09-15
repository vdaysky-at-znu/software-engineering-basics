import datetime
from uuid import UUID

import aiohttp


class CacheStore:
    def __init__(self):
        self._cache = {}

    def add(self, key, value):
        self._cache[key] = {"value": value, "added-at": datetime.datetime.now()}

    def time_check(self, key):
        cached_value = self._cache[key]
        now = datetime.datetime.now()
        if now - cached_value.get('added-at') < datetime.timedelta(hours=1):
            return True

        del self._cache[key]

    def _has(self, key):
        return key in self._cache

    def get(self, key):
        if self._has(key) and self.time_check(key):
            return self._cache[key]['value']


# uuid -> name
_uuid_cache = CacheStore()

# name -> uuid
_name_cache = CacheStore()


async def get_last_name(uuid) -> [str, None]:

    if uuid is None:
        return None

    if _uuid_cache.get(uuid):
        return _uuid_cache.get(uuid)

    async with aiohttp.ClientSession() as session:
        url = f'https://api.mojang.com/user/profiles/{uuid}/names'
        async with session.get(url) as response:

            if response.status != 200:
                print(await response.text())
                return None

            response = await response.json()

            if isinstance(response, dict) and response.get("error"):
                print(response)
                return None

            name = response[-1].get('name')
            _uuid_cache.add(uuid, name)
            return name


async def get_uuid(name) -> [None, UUID]:

    if name is None:
        return None

    if _name_cache.get(name):
        return _name_cache.get(name)

    url = f'https://api.mojang.com/users/profiles/minecraft/{name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            json = await response.json()
            uuid = UUID(json.get('id'))
            _name_cache.add(name, uuid)
            return uuid
