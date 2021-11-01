import enum
from datetime import datetime, timedelta

from . import mongo, api as ext_api

class Account:

    discord_user_id: str = None
    state: 'ACCOUNT_STATE' = None
    access_token: str = None
    access_token_type: str = None
    access_token_expiration: datetime = None
    refresh_token: str = None
    refresh_token_expiration: datetime = None
    created: datetime = None
    scopes: 'list[SCOPES]' = None
    redirect_url: str = None

    def __init__(self, discord_user_id: str = None):
        self._loaded = False
        self.discord_user_id = str(discord_user_id)
        self.state = ACCOUNT_STATE.UNKNOWN
        self.scopes = []

    def generate(self):
        '''Help initalize a fresh character.'''
        self.scopes = [scope for scope in SCOPES]
        self.redirect_url = 'https://poe.isbe.house/redirect'
        self.created = datetime.utcnow()
        self.state = ACCOUNT_STATE.UNREGISTERED

    def save(self, force: bool = False):
        '''Save account to Mongo.'''
        if not (self._loaded or force):
            print(self._loaded)
            print(force)
            raise RuntimeError('Cannot save an Account without a `force` or having loaded it first!')

        client = mongo.Mongo.client

        if self.discord_user_id is None:
            raise ValueError('Cannot save without a discord ID.')

        updates = {}
        updates.update({'state': self.state.name})
        updates.update({'access_token': self.access_token})
        updates.update({'access_token_expiration': self.access_token_expiration})
        updates.update({'refresh_token': self.refresh_token})
        updates.update({'created': self.created})
        updates.update({'scopes': [x.value for x in self.scopes]})

        client.accounts.discord_accounts.find_one_and_update(
            {
                'discord_user_id': self.discord_user_id
            },
            {
                '$set': {
                    **updates
                }
            },
            upsert=True,
        )

    def insert_character(self, character_id: str):

        client = mongo.Mongo.client

        client.accounts.discord_accounts.find_one_and_update(
            {
                'discord_user_id': self.discord_user_id
            },
            {
                '$addToSet': {
                    'characters': character_id
                }
            },
        )


    def load(self):
        '''Load account from Mongo.'''
        self._loaded = True
        client = mongo.Mongo.client

        if self.discord_user_id is None:
            raise ValueError('Cannot load without a discord ID.')

        account_doc = client.accounts.discord_accounts.find_one({'discord_user_id': self.discord_user_id})
        if account_doc is None:
            raise KeyError('No account found.')

        self.state = ACCOUNT_STATE[account_doc['state']]
        self.access_token = account_doc['access_token']
        self.access_token_expiration = account_doc['access_token_expiration']

    @property
    def bearer_token(self) -> str:
        '''Get users bearer token. Will refresh if needed.

        Raises:
            TimeoutError: User refresh token has expired, we need to ask for consent again.
        '''

        if (self.access_token is None) and (self.refresh_token is None):
            raise RuntimeError('Cannot fetch token, no access or refresh avliable.')

        if not isinstance(self.access_token_expiration, datetime):
            pass

        if self.access_token_expiration < datetime.utcnow():
            print(self.access_token_expiration)
            self.refresh_access_token()
            self.save()

        return self.access_token

    def ingest_authroization(self, data: dict):
        self.access_token = data['access_token']
        self.access_token_expiration = datetime.utcnow() + timedelta(seconds = data['expires_in']) - timedelta(hours = 1)
        self.token_type = data['token_type']
        self.scopes = [SCOPES(x) for x in data['scope'].split(' ')]
        self.refresh_token = data['refresh_token']
        self.refresh_token_expiration = datetime.utcnow() + timedelta(days = 90) - timedelta(hours = 1)

    def ingest_refresh(self, data: dict):
        self.access_token = data['access_token']
        self.access_token_expiration = datetime.utcnow() + timedelta(seconds = data['expires_in']) - timedelta(hours = 1) # We adjust this back an hour, just to be sure!
        self.access_token_type = data['token_type']
        self.scopes = [SCOPES(x) for x in data['scope'].split(' ')]

    def refresh_access_token(self):
        api = ext_api.API()
        refresh_dict = api.refresh_token(self.refresh_token)
        self.ingest_refresh(refresh_dict)
        self.save()

    def get_access_token(self, code: str):
        api = ext_api.API()
        token_dict = api.get_token(
            code,
            self.scopes,
            self.redirect_url,
        )
        self.ingest_authroization(token_dict)
        self.save()

    def generate_oauth_url(self):
        print(self.scopes)
        print([x.value for x in self.scopes])
        print()
        return ext_api.API().get_oauth_authorize_url(
            scopes=([str(x.value) for x in self.scopes]),
            state=self.discord_user_id,
            redirect_url=self.redirect_url,
        )

    async def get_leagues(self, limit=50, offset=0):
        return (await ext_api.API(bearer_token=self.bearer_token).get_leagues(limit, offset))

    async def get_profile(self):
        return (await ext_api.API(bearer_token=self.bearer_token).get_profile())

    async def get_characters(self):
        return (await ext_api.API(bearer_token=self.bearer_token).get_characters())

    async def get_character(self, name):
        return (await ext_api.API(bearer_token=self.bearer_token).get_character(name))

    async def get_stashes(self, league):
        return (await ext_api.API(bearer_token=self.bearer_token).get_stashes(league))


class Tokens:
    # TODO: Seperate tokens from account objects for secuirty.
    pass


class SCOPES(enum.Enum):
    ACCOUNT_PROFILE = 'account:profile'
    ACCOUNT_STASHES = 'account:stashes'
    ACCOUNT_CHARACTERS = 'account:characters'
    ACCOUNT_ITEM_FILTER = 'account:item_filter'


class ACCOUNT_STATE(enum.Enum):
    UNKNOWN = enum.auto()
    UNREGISTERED = enum.auto()
    REGISTERING = enum.auto()
    REGISTERED = enum.auto()
    EXPIRED = enum.auto()
    REVOKED = enum.auto()
    BANNED = enum.auto()
