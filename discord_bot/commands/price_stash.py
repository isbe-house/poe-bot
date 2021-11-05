from dyscord.objects.base_object import BaseDiscordObject
from dyscord.objects.interactions import Interaction
from poe_lib import API, Account
import difflib

class PriceStash:

    def __init__(self, interaction: Interaction, account: Account):
        self.interaction = interaction
        self.account = account
        self.api = API(bearer_token = account.bearer_token)

    async def __call__(self):
        if self.interaction.type == self.interaction.INTERACTION_TYPES.APPLICATION_COMMAND_AUTOCOMPLETE:
            await self.handle_auto_complete()
            return

        desired_stash = self.interaction.data.options['price_stash']['name'].value
        league = self.interaction.data.options['price_stash']['league'].value

        stashes = await self.api.get_stashes(league)

        for stash in stashes:
            if stash.name == desired_stash:
                break
        else:
            response = self.interaction.generate_response()
            response.generate('Well this kinda sucks, seems Soton hasn\'t coded this in yet....', ephemeral=True)
            await response.send()
            return

        stash = await self.api.get_stash(league, stash.id)

        print(stash.__dict__)

    async def handle_auto_complete(self):

        if 'league' in self.interaction.data.options['price_stash'] and self.interaction.data.options['price_stash']['league'].focused:
            await self.handle_auto_complete_league()

        elif 'name' in self.interaction.data.options['price_stash'] \
            and 'league' in self.interaction.data.options['price_stash'] \
            and self.interaction.data.options['price_stash']['name'].focused:

            await self.handle_auto_complete_stash()

    async def handle_auto_complete_league(self):

        response = self.interaction.generate_response(self.interaction.INTERACTION_RESPONSE_TYPES.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT)
        leagues = [x.id for x in await API().get_leagues()]
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
