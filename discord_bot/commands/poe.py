import dyscord
from dyscord.objects import interactions
from poe_lib import Account

from ..mongo import Mongo

from . import profile, register, character, price_stash

async def poe_callback(interaction: dyscord.objects.interactions.Interaction):

    if interaction.data is None:
        raise TypeError

    account = Account(interaction.member.id)  # type: ignore
    account.load()

    if 'profile' in interaction.data.options:
        return await profile.profile_callback(interaction)

    elif 'register' in interaction.data.options:
        return await register.registration_callback(interaction)

    elif 'character' in interaction.data.options:
        return await character.character_callback(interaction)

    elif 'price_stash' in interaction.data.options:
        return await price_stash.PriceStash(interaction, account)()  # We can't have async __init__ so we fake it with a __call__()

    else:
        response = interaction.generate_response()
        response.generate('Well this kinda sucks, seems Soton hasn\'t coded this in yet....', ephemeral=True)
        await response.send()
