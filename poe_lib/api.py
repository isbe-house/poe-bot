import datetime
import asyncio
import enum
from pprint import pprint

import httpx

from . import __version__

class API:

    BASE_URL = 'https://api.pathofexile.com'
    _lock = asyncio.Lock()

    class ERROR_CODES(enum.IntEnum):
        ACCEPTED = 0
        RESOURCE_NOT_FOUND = 1
        INVALID_QUERY = 2
        RATE_LIMIT_EXCEEDED = 3
        INTERNAL_ERROR = 4
        UNEXPECTED_CONTENT_TYPE = 5
        UNAUTHORIZED = 8
        FORBIDDEN = 6
        TEMPORARILY_UNAVAILABLE = 7
        METHOD_NOT_FOUND = 9
        UNPROCESSABLE_ENTITY = 10

    def __init__(self, client_id: str):
        self.client_id = client_id

    def oauth_authorize(self, scopes: 'list[str]', state: str, redirect_url: str, prompt: str = 'consent'):

        params = {
            'client_id':  self.client_id,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
            'redirect_uri': redirect_url,
            'prompt': prompt,
        }

        client = httpx.Client()
        request = client.build_request('GET', self.BASE_URL + '/oauth/authorize', params = params)

        return request


    @property
    def user_agent(self):
        return f'OAuth {self.client_id}/{__version__} (contact: jmurrayufo@gmail.com)'

    @classmethod
    async def _handle_rate_limit(cls, response):
        headers = response.headers
        # Determine which rule we need to follow

        rule = headers['X-Rate-Limit-Rules']

        limit = headers[f'X-Rate-Limit-{rule}'].split(':')
        state = headers[f'X-Rate-Limit-{rule}-State'].split(':')

        limit = [int(x) for x in limit]
        state = [int(x) for x in state]

        if state[2]:
            await asyncio.sleep(state[2])
            return

        percent_hits = (state[0]/limit[0])**10
        time_to_sleep = percent_hits * state[1] * 1.1
        if time_to_sleep > 0.1:
            # print(f'Sleeping {time_to_sleep:.3f} due to {state}')

            await asyncio.sleep(time_to_sleep)

        return

    @classmethod
    async def _invoke_method(cls, method):
        async with cls._lock:
            r = await method
            try:
                r.raise_for_status()
            except Exception:
                raise
            await cls._handle_rate_limit(r)
        return r

    async def get_leagues(self, realm: str = 'pc', type: str = 'main', limit: int = 50, offset: int = 0):
        url = self.BASE_URL + '/league'


    async def public_stash_tabs(self, next_change_id: str = None):
        url = self.BASE_URL + '/public-stash-tabs'

        params = dict()
        if next_change_id is not None:
            params['id'] = next_change_id

        async with httpx.AsyncClient() as client:
            method =  client.get(url, params = params)
            r = await self._invoke_method(method)

        return r.json()
