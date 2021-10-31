import uuid
import poe_lib


with open('/run/secrets/discord_client_id') as fp:
    client_id = fp.read()

with open('/run/secrets/discord_client_secret') as fp:
    client_secret = fp.read()

x = poe_lib.api.API(client_id)

print(
    x.get_oauth_authorize_url(
        scopes=['account:profile','account:characters','account:item_filter','account:stashes'],
        state=str(uuid.uuid4()),
        redirect_url='https://poe.isbe.house/redirect',
    ).url
)

r = x.get_client_grant(client_id, client_secret)

print(r.json())