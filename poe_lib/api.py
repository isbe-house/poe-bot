import datetime
import asyncio
import enum
from pprint import pprint
import os
from typing import List, Optional
from cachetools import TTLCache

import httpx

from . import __version__

from .objects import character, leagues, stash, profile
from . import log

class API:

    _call_hash = TTLCache(float('inf'), ttl=300)

    client_id: str = None
    bearer_token: Optional[str] = None
    client_secret: str = None
    client_token: str = None

    BASE_URL = 'https://api.pathofexile.com'
    AUTH_URL = 'https://www.pathofexile.com'

    _lock = asyncio.Lock()

    log = log.Log()

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

    def __init__(self, client_id: str = None, bearer_token: Optional[str] = None, client_secret: str = None, client_token: str = None):
        self.client_id = client_id if client_id is not None else os.environ.get('POE_CLIENT_ID', None)
        self.bearer_token = bearer_token
        self.client_token = client_token if client_token is not None else os.environ.get('POE_CLIENT_TOKEN', None)
        self.client_secret = client_secret if client_secret is not None else os.environ.get('POE_CLIENT_SECRET', None)
        self.verbose = False

    def get_oauth_authorize_url(self, scopes: 'list[str]', state: str, redirect_url: str, prompt: str = 'consent'):
        '''Get auth URL to give to a registering user.'''

        params = {
            'client_id':  self.client_id,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
            'redirect_uri': redirect_url,
            'prompt': prompt,
        }

        client = httpx.Client()
        request = client.build_request('GET', self.AUTH_URL + '/oauth/authorize', params = params)

        return request.url

    def get_client_grant(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'service:psapi service:leagues',
        }

        r = httpx.post(
            self.AUTH_URL + '/oauth/token',
            json = params,
            headers = self.get_headers(),
        )

        return r

    def get_token(self, code: str, scopes: list[str], redirect_url: str) -> dict:
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'scope': ' '.join(scopes),
            'redirect_url': redirect_url,
        }

        r = httpx.post(
            url = self.AUTH_URL + '/oauth/token',
            json = params,
            headers=self.get_headers(),
        )
        r.raise_for_status()
        return r.json()

    def refresh_token(self, refresh_token: str) -> dict:
        '''Refresh token from Path of Exile API.
        This returns a dict like:
        {
            "access_token": "41bcefbc2f0d6ea0fa1cce10c435310d3c475e5b",
            "expires_in": 2592000,
            "token_type": "bearer",
            "scope": "account:profile"
        }
        '''
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        r = httpx.post(
            url = self.AUTH_URL + '/oauth/token',
            json = params,
        )
        r.raise_for_status()
        return r.json()

    @property
    def user_agent(self) -> dict:
        return {'User-Agent': f'OAuth {self.client_id}/{__version__} (contact: jmurrayufo@gmail.com)'}

    @property
    def auth_header(self) -> dict:
        return {'Authorization': f'Bearer {self.bearer_token}'}

    @property
    def client_token_header(self) -> dict:
        return {'Authorization': f'Bearer {self.client_token}'}

    def get_headers(self, use_client_token: bool = False) -> dict:
        headers = {}
        headers.update(self.user_agent)
        if self.bearer_token is not None:
            headers.update(self.auth_header)
        if use_client_token:
            headers.update(self.client_token_header)
        return headers

    async def _handle_rate_limit(self, response):
        headers = response.headers
        # Determine which rule we need to follow

        try:
            rules = headers['X-Rate-Limit-Rules']
        except KeyError:
            return

        time_to_sleep = 0
        self.log.debug('Handling rate limits.')
        self.log.debug(headers)

        for rule in rules.split(','):
            self.log.debug(f'Handle limits for {rule}.')

            if 'Retry-After' in headers:
                sleep_for = float(headers['Retry-After']) * 2
                self.log.debug(f'Encountered [Retry-After] header. Sleep for [{sleep_for}].')
                await asyncio.sleep(sleep_for)
                return

            limits = headers[f'X-Rate-Limit-{rule}'].split(',')
            states = headers[f'X-Rate-Limit-{rule}-State'].split(',')

            for limit, state in zip(limits, states):
                limit = [int(x) for x in limit.split(':')]
                state = [int(x) for x in state.split(':')]

                # print(f'{state[0]} / {limit[0]} in {state[1]}:{limit[1]}')

                time_to_sleep = max(time_to_sleep, state[2])

                percent_hits = (state[0]/limit[0])**10
                time_to_sleep = max(percent_hits * state[1] * 1.1, time_to_sleep)

        if time_to_sleep > 0.1:
            self.log.debug(f'Sleeping for {time_to_sleep} becuase of {rules}')
            await asyncio.sleep(time_to_sleep)

        return

    async def _invoke_method(self, method):
        async with self._lock:
            r = await method
            try:
                r.raise_for_status()
            except Exception as e:
                print(f'Exception Raised: {e}')
                print(f'Headers: {r.headers}')
                raise
            await self._handle_rate_limit(r)
        return r

    async def public_stash_tabs(self, next_change_id: str = None):
        url = self.BASE_URL + '/public-stash-tabs'

        params = dict()
        if next_change_id is not None:
            params['id'] = next_change_id

        async with httpx.AsyncClient() as client:
            method = client.get(url, params = params, headers=self.get_headers(use_client_token=True))
            r = await self._invoke_method(method)

        return r.json()

    async def get_leagues(self, realm: str = 'pc', type: str = 'main', limit: int = 50, offset: int = 0) -> 'List[leagues.League]':
        url = self.BASE_URL + '/league'

        hash_key = (url, str(self.get_headers()), realm, type, limit, offset)
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, params = {'realm': realm, 'type': type, 'limit': limit, 'offset': offset}, headers=self.get_headers(use_client_token=True))
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r

        return [leagues.League(x) for x in r.json()['leagues']]

    async def get_league(self, league: str, realm: str = 'pc') -> 'leagues.League':
        url = self.BASE_URL + f'/league/{league}'

        hash_key = (url, str(self.get_headers()), realm, league)
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, params = {'realm': realm}, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r

        return leagues.League(r.json()['league'])

    async def get_profile(self) -> 'profile.Profile':
        url = self.BASE_URL + "/profile"

        hash_key = (url, str(self.get_headers()))
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r

        return profile.Profile(r.json())

    async def get_characters(self) -> List[character.Character]:
        url = self.BASE_URL + "/character"

        hash_key = (url, str(self.get_headers()))
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r
        return [character.Character(x) for x in r.json()['characters']]

    async def get_character(self, name: str) -> character.Character:
        url = self.BASE_URL + f"/character/{name}"

        hash_key = (url, str(self.get_headers()))
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r
        return character.Character(r.json()['character'])

    async def get_stashes(self, league: str) -> 'List[stash.Stash]':
        url = self.BASE_URL + f"/stash/{league}"

        hash_key = (url, str(self.get_headers()))
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r
        return [stash.Stash(x) for x in r.json()['stashes']]

    async def get_stash(self, league: str, stash_id: str, substash_id: Optional[str] = None) -> 'stash.Stash':
        url = self.BASE_URL + f"/stash/{league}/{stash_id}"
        if substash_id is not None:
            url += f'/{substash_id}'

        hash_key = (url, str(self.get_headers()))
        try:
            r = self._call_hash[hash_key]
        except KeyError:
            async with httpx.AsyncClient() as client:
                method = client.get(url, headers=self.get_headers())
                r = await self._invoke_method(method)
        self._call_hash[hash_key] = r
        return stash.Stash(r.json()['stash'])
