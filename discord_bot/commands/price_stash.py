from dyscord.objects import interactions
from dyscord.objects.base_object import BaseDiscordObject
from dyscord.objects.interactions import Interaction
from poe_lib import API, Account
import difflib
import datetime

from ..mongo import Mongo

class PriceStash:

    def __init__(self, interaction: Interaction, account: Account):
        self.interaction = interaction
        self.account = account
        self.api = API(bearer_token = account.bearer_token)

    async def __call__(self):
        if self.interaction.type == self.interaction.INTERACTION_TYPES.APPLICATION_COMMAND_AUTOCOMPLETE:
            await self.handle_auto_complete()
            return

        ephemeral = not self.interaction.data.options['price_stash'].get('public', False)
        full_stats = self.interaction.data.options['price_stash'].get('full_stats', False)
        desired_stash = self.interaction.data.options['price_stash']['name'].value
        league = self.interaction.data.options['price_stash']['league'].value

        stashes = await self.api.get_stashes(league)

        for stash in stashes:
            if stash.name == desired_stash:
                break
        else:
            response = self.interaction.generate_response()
            response.generate('Well this kinda sucks, seems Soton hasn\'t coded this in yet....', ephemeral=ephemeral)
            await response.send()
            return

        stash = await self.api.get_stash(league, stash.id)

        total_value = 0.0
        uncertaincy = 0.0
        skipped_items = 0
        counted_items = 0

        most_valued = {'item': None, 'value': -1, 'std': 0}

        client = Mongo.async_client

        for item in stash.items:
            cost = await client.trade.cost_estimates.find_one({'typeLine': item.typeLine}, projection={'typeLine': 1, 'std': 1, 'value': 1, '_id': 0})
            if cost is None:
                skipped_items += 1
                continue

            if cost['std'] > cost['value']:
                skipped_items += 1
                continue

            counted_items += item.stackSize
            total_value += cost['value'] * item.stackSize
            uncertaincy += cost['std'] * item.stackSize

            if cost['value'] * item.stackSize > most_valued['value']:
                most_valued = {'item': item, 'value': cost['value'] * item.stackSize, 'std': cost['std'] * item.stackSize}

        response = self.interaction.generate_response(ephemeral=ephemeral)
        if self.interaction.member is not None:
            response.generate(f'{self.interaction.member.mention}, here is your stash estimate.')
        elif self.interaction.user is not None:
            response.generate(f'{self.interaction.user.mention}, here is your stash estimate.')
        else:
            response.generate('Here is your stash estimate!')
        embeds = response.add_embeds()
        embeds.generate(f'Stash Tab: {desired_stash}', timestamp=datetime.datetime.utcnow())
        embeds.add_field('Total Value', f'{total_value:,.1f} ₡')
        embeds.add_field('Uncertaincy', f'+/- {uncertaincy:,.1f} ₡')
        if full_stats:
            embeds.add_field('Most Valued', most_valued['item'].typeLine)
            embeds.add_field('Most Valued Value', f'{most_valued["value"]:,.0f} ₡')
            embeds.add_field('Most Valued STD', f'+/- {most_valued["std"]:,.0f} ₡')
            embeds.add_field('Items Counted', f'{counted_items:,}')
            embeds.add_field('Items Skipped', f'{skipped_items:,}')
        await response.send()

    async def handle_auto_complete(self):

        if 'league' in self.interaction.data.options['price_stash'] and self.interaction.data.options['price_stash']['league'].focused:
            await self.handle_auto_complete_league()

        elif 'name' in self.interaction.data.options['price_stash'] \
            and 'league' in self.interaction.data.options['price_stash'] \
            and self.interaction.data.options['price_stash']['name'].focused:

            await self.handle_auto_complete_stash()

    async def handle_auto_complete_league(self):

        response = self.interaction.generate_response(self.interaction.INTERACTION_RESPONSE_TYPES.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT)
        leagues = [x.id for x in await self.api.get_leagues()]
        assert self.interaction.data is not None

        best_matches = difflib.get_close_matches(self.interaction.data.options['price_stash']['league'].value, leagues, 25, cutoff=0)
        response.add_choices()

        for match in best_matches:
            response.add_choice(match, match)

        await response.send()

    async def handle_auto_complete_stash(self):

        response = self.interaction.generate_response(self.interaction.INTERACTION_RESPONSE_TYPES.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT)
        stashes = await self.api.get_stashes(self.interaction.data.options['price_stash']['league'].value)
        stashes = [x.name for x in stashes]

        best_matches = difflib.get_close_matches(self.interaction.data.options['price_stash']['name'].value, stashes, 25, cutoff=0)
        response.add_choices()

        for match in best_matches:
            response.add_choice(match, match)

        await response.send()
