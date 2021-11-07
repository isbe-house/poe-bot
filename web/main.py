from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

import datetime
import mongo
import poe_lib
import os

with open('/run/secrets/client_id') as fp:
    os.environ['POE_CLIENT_ID'] = fp.read()
with open('/run/secrets/client_secret') as fp:
    os.environ['POE_CLIENT_SECRET'] = fp.read()

app = FastAPI()

@app.get("/redirect", response_class=HTMLResponse)
async def handle_redirect(code: str, state: str, invalid_request: str=None):
    client = mongo.Mongo.client

    print(f'Saw registration with state [{state}] and code [{code}].')

    account = poe_lib.Account(str(state))
    try:
        account.load()
    except KeyError:
        return HTTPException(status_code=403, detail="State has been modified, registration rejected.")

    account.state = poe_lib.ACCOUNT_STATE.REGISTERING
    account.save()

    poe_api = poe_lib.api.API()

    user_secrets = poe_api.get_token(
        code,
        [scope.value for scope in account.scopes],
        account.redirect_url,
    )

    account.ingest_authroization(user_secrets)

    # Try to get profile
    poe_api = poe_lib.api.API(bearer_token=account.bearer_token)

    profile = await poe_api.get_profile()
    account.poe_account_name = profile.name

    # Get characters
    for character in await poe_api.get_characters():
        account.insert_character(character.id)

    account.state = poe_lib.ACCOUNT_STATE.REGISTERED
    account.save()

    return "Your account was <b>registered</b>! You can close this window and use the other bot commands."

# This is needed for certbot to work!
app.mount("/", StaticFiles(directory="static"), name="static")

mongo.Mongo.connect()