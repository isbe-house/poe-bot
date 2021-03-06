import asyncio
import datetime
import os
import logging

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
with open('/run/secrets/client_token') as fp:
    os.environ['POE_CLIENT_TOKEN'] = fp.read()

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
    sc = register_command.add_option_sub_command(name='register', description='Register with the bot.')

    sc = register_command.add_option_sub_command(name='profile', description='Print your profile.')

    sc = register_command.add_option_sub_command(name='character', description='Show off your character.')

    sc = register_command.add_option_sub_command(name='price_stash', description='Calculate estimated value of a stash.')
    sc.add_option_typed(sc.COMMAND_OPTION.STRING, name='league', description='League stash is in', autocomplete=True, required=True)
    sc.add_option_typed(sc.COMMAND_OPTION.STRING, name='name', description='Stash name/regex.', required=True, autocomplete=True)
    sc.add_option_typed(sc.COMMAND_OPTION.BOOLEAN, name='full_stats', description='Should you be provided with full information?', required=False)
    sc.add_option_typed(sc.COMMAND_OPTION.BOOLEAN, name='public', description='Can other people see this?', required=False)

    sc = register_command.add_option_sub_command(name='test', description='Test command, please ignore.')

    register_command.validate()
    await register_command.register_to_guild('346094316428591104')

    # print('Remove global commands')
    # commands = await API.get_global_application_commands()
    # for command in commands:
    #     print(command)
    #     command = dyscord.objects.interactions.Command().from_dict(command)
    #     assert command.id is not None
    #     await API.delete_global_application_command(command.id)

dyscord.helper.CommandHandler.register_guild_callback('poe', poe_callback)

async def raw_back(data):
    print(data)

# client._register_raw_callback(raw_back)
log = logging.getLogger('dyscord')
log.setLevel(logging.INFO)
client.run()