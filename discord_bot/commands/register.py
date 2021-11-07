import datetime

import poe_lib

from ..mongo import Mongo

async def registration_callback(interaction):
    # Check to see if this person is already in the DB.

    client = Mongo.client
    discord_user_id = interaction.member.id
    account = poe_lib.Account(discord_user_id)
    response = interaction.generate_response()

    account.generate()
    auth_url = account.generate_oauth_url()

    response.generate(f'Please visit {auth_url} to register with POE\'s OAUTH.', ephemeral=True)
    await response.send()

    account.save()
