import datetime

import poe_lib

from ..mongo import Mongo

async def character_callback(interaction):
    # Check to see if this person is already in the DB.
    discord_user_id = interaction.member.id
    account = poe_lib.Account(discord_user_id)
    response = interaction.generate_response()

    try:
        account.load()
        # If we got here, error our
    except KeyError:
        response = interaction.generate_response()
        response.generate('You doon\'t have an active account, run `/poe register` to fix that!', ephemeral=True)
        await response.send()
        return

    characters = await account.get_characters()
    for character in characters:
        print(character.__dict__)
        character.save()
        account.insert_character(character.id)

    response.generate('Command executed, check logs!', ephemeral=True)
    await response.send()
