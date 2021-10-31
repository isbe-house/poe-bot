import dyscord
import poe_lib

from ..mongo import Mongo


async def profile_callback(interaction: dyscord.objects.interactions.Interaction):
    client = Mongo.client

    discord_user_id = interaction.member.id

    account = poe_lib.Account(discord_user_id)
    try:
        account.load()
    except KeyError:
        response = interaction.generate_response()
        response.generate('You doon\'t have an active account, run `/poe register` to fix that!', ephemeral=True)
        await response.send()
        return

    # Invoke poe_api
    api = poe_lib.api.API(bearer_token = account.bearer_token)

    profile = await api.get_profile()

    response = interaction.generate_response()
    response.generate()
    embed = response.add_embeds()
    embed.generate(f'{profile["name"]}')
    embed.add_field('Realm', profile['realm'])
    await response.send()

    x = await account.get_stashes('Standard')
