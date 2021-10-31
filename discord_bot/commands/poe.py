import dyscord
from dyscord.objects import interactions

from ..mongo import Mongo

from . import profile, register

async def poe_callback(interaction: dyscord.objects.interactions.Interaction):

    if 'profile' in interaction.data.options:
        return await profile.profile_callback(interaction)

    if 'register' in interaction.data.options:
        return await register.registration_callback(interaction)
