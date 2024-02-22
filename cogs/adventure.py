import discord
from discord import app_commands
from discord.ext import commands
from cogs.utils.keywords import Keyword as ky
import cogs.utils.user_utils as user_utils
from cogs.utils.bot_utils import Emojis as emoji, Item, create_error_response
# from cogs.dungeons.corrupted_gauntlet import CorruptedGauntlet
from OSRSBytes import Items as OSRSItems
from random import randint, random
from typing import Optional
from enum import Enum


class SellButton(discord.ui.View):
    def __init__(self, game_instance, embed):
        super().__init__(timeout=30)
        self.game_instance = game_instance
        self.embed = embed
        self.interaction = game_instance.interaction
        self.user = game_instance.interaction.user
        self.drops = game_instance.drops
        self.total_value = game_instance.total_value
        self.sell_drops.label = f"Sell All ({self.total_value:,})"


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.interaction.user.id == interaction.user.id

    
    def add_items_to_user_inventory(self):
        """Adds items to the instance's user."""
        for item in self.drops:
            user_utils.add_item(self.user, item=item)


    @discord.ui.button(label="Keep All", emoji="\U0001F4E6", style=discord.ButtonStyle.primary)
    async def keep_drops(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        self.add_items_to_user_inventory()
        self.stop()


    async def on_timeout(self):
        interaction_message = await self.interaction.original_response()
        for child in self.children:
            child.disabled = True
        await interaction_message.edit(view=None)
        self.add_items_to_user_inventory()
        self.stop()


    @discord.ui.button(label="Sell All", emoji=emoji.CURRENCY, style=discord.ButtonStyle.green)
    async def sell_drops(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.add_field(
            name="You've sold your rewards on the Grand Exchange!",
            value=f"A buyer purchased your {len(self.drops):,} item(s) for {self.total_value:,} {emoji.CURRENCY}.",
            inline=False
        )
        user_utils.add_balance(self.user, self.total_value)
        await interaction.response.edit_message(embed=self.embed, view=None)
        self.stop()


class Rewards:
    def __init__(self):
        self.grand_exchange = OSRSItems()
        self.table = {
            "Crystal Shard": { "data": Item(name="Crystal Shard", icon="<:crystal_shard:888531512461508628>"), "rarity": 0 },
            "Crystal Weapon Seed": { "data": Item(name="Crystal Weapon Seed", icon="<:crystal_weapon_seed:888531512394383370>"), "rarity": 0.05, "id": "4207" },
            "Crystal Armour Seed": { "data": Item(name="Crystal Armour Seed", icon="<:crystal_armour_seed:888531512209866824>"), "rarity": 0.05, "id": "23956" },
            "Enhanced Crystal Weapon Seed": { "data": Item(name="Enhanced Crystal Weapon Seed", icon="<:enhanced_crystal_weapon_seed:888531512201449542>"), "rarity": 0.0025, "id": "25859" },
            "Youngllef": { "data": Item(name="Youngllef", icon="<:youngllef:888531512591527997>"), "rarity": 0.00125 }
        }


    def drop_crystal_shards(self):
        """Drops a random number of Crystal Shards. This returns a tuple containing the Item data for Crystal Shards and the quantity
        dropped."""
        MINIMUM_DROPS = 5
        MAXIMUM_DROPS = 9
        quantity = randint(MINIMUM_DROPS, MAXIMUM_DROPS)
        return (self.table["Crystal Shard"]["data"], quantity)


    def drop_rewards(self):
        """Returns a randomized list of rewards, not including Crystal Shards. This returns a tuple containing a list of Item objects and
        their total value."""
        drops = []
        total_value = 0
        drop_table = self.table
        drop_table.pop("Crystal Shard", None)  # crystal shards are dropped via drop_crystal_shards()
        for item in drop_table.keys():
            if random() < drop_table[item]["rarity"]:
                drops.append(drop_table[item]["data"])
                if item != "Youngllef":
                    total_value += self.get_value(item)
        return (drops, total_value)


    def get_value(self, item_name):
        """Uses OSRSBytes to retrieve the sell average of an item."""
        return int(self.grand_exchange.getSellAverage(self.table[item_name]["id"]) / 100)


class CorruptedGauntlet:
    def __init__(self, interaction):
        self.interaction = interaction
        self.user = interaction.user
        self.drops = []
        self.total_value = 0
        self.views_enabled = False


    def play(self):
        """The main game mechanism. Runs through the logic of the slot game and returns an discord.Embed message that describes the results of the adventure."""
        if not user_utils.is_registered(self.user):
            return create_error_response(message="You're not registered! Use `/register` first to participate in economy-related features.)")

        rewards = Rewards()
        crystal_shard, crystal_shard_quantity = rewards.drop_crystal_shards()
        user_utils.add_item(self.user, item=crystal_shard, quantity=crystal_shard_quantity)
    
        self.drops, self.total_value = rewards.drop_rewards()

        completion_count = user_utils.increment_completion_count(self.user, key="corrupted_gauntlet")
        description = f"Your Corrupted Gauntlet completion count is **{completion_count:,}**"
        embed = discord.Embed(title="You've braved the Corrupted Gauntlet", description=description)

        drop_messages = [f"{crystal_shard.icon} {crystal_shard_quantity}×{crystal_shard.name} (Untradeable)"]
        for item in self.drops:
            message = f"{item.icon} 1×{item.name}"
            value = rewards.get_value(item.name)
            message = f"{message} (Sell Average: {value:,} {emoji.CURRENCY})" if value != -1 else f"{message} (Untradeable)"
            if item.name == "Youngllef":  # Youngllef is untradable, so add it to the user's inventory, then remove it from the list of drops.
                user_utils.add_item(self.user, item=item)
                self.drops.remove(item)
            drop_messages.append(message)

        if self.total_value > 0:  # Only display sell information if the user obtained loot that can be sold.
            self.views_enabled = True
            sell_message = f"Untradeable drops have been stored into your inventory. You may choose to also store the remaining items, or sell them instead."
            embed.set_footer(text="If you do not make a decision after 30 seconds, all drops will be automatically stored into your inventory.")
            drop_messages.append(sell_message)

        embed.add_field(name="**You find some treasure!**", value="\n".join(drop_messages))
        return embed

            

class Adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def cooldown_for_non_registered_user(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
        '''Prevents a cooldown from being invoked when a non-registered user attempts to use a command that requires registration.'''
        return app_commands.Cooldown(1, 600) if user_utils.is_registered(interaction.user) else None
        

    adventures = app_commands.Group(name="go", description="Go on an adventure!")

    @app_commands.checks.dynamic_cooldown(cooldown_for_non_registered_user)
    @adventures.command(name="gauntlet", description="Visit the Corrupted Gauntlet.")
    async def corrupted_gauntlet(self, interaction: discord.Interaction):
        corrupted_gauntlet = CorruptedGauntlet(interaction)
        embed = corrupted_gauntlet.play()
        file = discord.File("/home/ec2-user/frostnova/cogs/_images/corrupted_gauntlet.png", filename="corrupted_gauntlet.png")
        embed.set_image(url="attachment://corrupted_gauntlet.png")
        if corrupted_gauntlet.views_enabled:  # passing view=None will trigger a CommandInvokeError on send_message
            await interaction.response.send_message(embed=embed, file=file, view=SellButton(game_instance=corrupted_gauntlet, embed=embed, file=self.file))
        else:
            await interaction.response.send_message(embed=embed, file=file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Adventure(bot))
