from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

import datetime
import mongo
import poe_lib

with open('/run/secrets/client_id') as fp:
    client_id = fp.read()
with open('/run/secrets/client_secret') as fp:
    client_secret = fp.read()

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

    poe_api = poe_lib.api.API(client_id=client_id, client_secret=client_secret)

    user_secrets = poe_api.get_token(
        code,
        [scope.value for scope in account.scopes],
        account.redirect_url,
    )

    account.ingest_authroization(user_secrets)
    account.save()

    return "Your account was <b>registered</b>! You can close this window and use the other bot commands."

# This is needed for certbot to work!
app.mount("/", StaticFiles(directory="static"), name="static")

mongo.Mongo.connect()