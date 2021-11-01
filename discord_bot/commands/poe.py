import dyscord
from dyscord.objects import interactions

from ..mongo import Mongo

from . import profile, register, character

async def poe_callback(interaction: dyscord.objects.interactions.Interaction):

    if 'profile' in interaction.data.options:
        return await profile.profile_callback(interaction)

    elif 'register' in interaction.data.options:
        return await register.registration_callback(interaction)

    elif 'character' in interaction.data.options:
        return await character.character_callback(interaction)

    else:
        response = interaction.generate_response()
        response.generate('Well this kinda sucks, seems Soton hasn\'t coded this in yet....', ephemeral=True)
        await response.send()
