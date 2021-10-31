import asyncio
import datetime
import os

import dyscord
from dyscord.client import API
import poe_lib

from .mongo import Mongo
from .commands import profile_callback, poe_callback, registration_callback

with open('/run/secrets/discord_bot_token') as fp:
    token = fp.read()
with open('/run/secrets/discord_application_id') as fp:
    application_id = fp.read()
with open('/run/secrets/client_id') as fp:
    os.environ['POE_CLIENT_ID'] = fp.read()

client = dyscord.client.DiscordClient(token, application_id)

client.set_all_intents()

@client.decorate_handler('READY')
async def my_ready(ready, _, client):

    if True:
        print('Skipping command registrations.')
        for command in await API.get_global_application_commands():
            print(command)
        return

    print('REGISTER!')
    register_command = dyscord.objects.interactions.Command()
    register_command.generate(
        name='poe',
        description='Path of exile.',
        type=dyscord.objects.interactions.enumerations.COMMAND_TYPE.CHAT_INPUT,
    )
    register_command.add_option_sub_command(name='register', description='Register with the bot.')
    register_command.add_option_sub_command(name='profile', description='Print your profile.')
    register_command.validate()
    await register_command.register_globally()


    # print('Remove global commands')
    # commands = await API.get_global_application_commands()
    # for command in commands:
    #     print(command)
    #     command = dyscord.objects.interactions.Command().from_dict(command)
    #     assert command.id is not None
    #     await API.delete_global_application_command(command.id)


Mongo.connect()

dyscord.helper.CommandHandler.register_global_callback('register', registration_callback)
dyscord.helper.CommandHandler.register_global_callback('profile', profile_callback)
dyscord.helper.CommandHandler.register_global_callback('poe', poe_callback)

client.run()