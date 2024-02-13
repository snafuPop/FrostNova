import discord
from discord import app_commands
from discord.ext import commands
from cogs.utils.keywords import Keyword as ky
import cogs.utils.user_utils as user_utils
import cogs.utils.bot_utils as bot_utils
from random import randint, shuffle
from typing import Optional
from enum import Enum


class ReplayButton(discord.ui.View):
    def __init__(self, slot_game):
        super().__init__(timeout=None)
        self.slot_game = slot_game
        self.interaction = slot_game.interaction
        self.wager = slot_game.wager
        self.play_again.label = f"Play Again (Wager: {self.wager:,})"

    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.interaction.user.id == interaction.user.id


    @discord.ui.button(label="Play Again", emoji="\U0001F501", style=discord.ButtonStyle.success)
    async def play_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        # embed = self.play_slots(interaction, wager)
        # await interaction.response.edit_message(embed=embed)
        embed = self.slot_game.play()
        await interaction.response.edit_message(embed=embed)


class Reel(dict):
    def __init__(self, *arg, **kwargs):
        super(Reel, self).__init__(*arg, **kwargs)
        self.reel_dictionary = {
            "cherries": {"emoji": ":cherries:", "payout": 10, "count": 20},
            "bell": {"emoji": ":bell:", "payout": 10, "count": 30},
            "diamond": {"emoji": ":diamond_shape_with_a_dot_inside:", "payout": 20, "count": 25},
            "seven": {"emoji": ":seven:", "payout": 30, "count": 20},
            "lemon": {"emoji": ":lemon:","payout": 40,"count": 12},
            "grapes": {"emoji": ":grapes:","payout": 60,"count": 8},
            "orange": {"emoji": ":tangerine:","payout": 100,"count": 4},
            "secret": {"emoji": "<a:w_:1205606672970686545>","payout": 1000000,"count": 1}
        }


    def get_keys(self, sort_keys: bool=False):
        """Returns a list of all the keys in the reel dictionary. If sort_keys is True, then the keys will be ordered by their payout
        values in ascending order."""
        return sorted(self.reel_dictionary.keys(), key=lambda x: self.reel_dictionary[x]["payout"]) if sort_keys else list(self.reel_dictionary.keys())


    def get_emoji(self, key):
        """Returns the emoji of a specified symbol."""
        return self.reel_dictionary[key]["emoji"]

    
    def get_payout(self, key):
        """Returns the payout value (i.e., the amount the wager is multiplied by) of a specified symbol."""
        return self.reel_dictionary[key]["payout"]

    
    def get_count(self, key):
        """Returns the count (i.e., the number of times it appears in a reel) of a specified symbol."""
        return self.reel_dictionary[key]["count"]


class SlotGame:
    def __init__(self, interaction, wager):
        self.reel = Reel()
        self.interaction = interaction
        self.user = interaction.user
        self.wager = wager


    def create_reel(self):
        """Rather than randomly selecting a symbol, generate an ordered list of random symbols,  then pick a random symbol from that list.
        This simulates a phyhsical reel, in which symbols are at a fixed location."""
        reel = [key for key in self.reel.get_keys() for i in range(self.reel.get_count(key))]
        shuffle(reel)
        return reel


    def pick_random_triplet_in_reel(self, reel):
        """Picks a random triplet on the reel, circularly. The 0th index represents the top of the reel, and the 2nd index represents the
        bottom."""
        index = randint(0, len(reel) - 1)
        return [reel[(index - 1) % len(reel)], reel[index], reel[(index + 1) % len(reel)]]


    def determine_payout(self, slot_output, wager):
        """Given the output of a slot machine play, determine the payout. This is returned as a tuple
        (payout message, amount to be paid out)."""
        payout_line = [slot_output[0][1], slot_output[1][1], slot_output[2][1]]
        if all(value == payout_line[0] for value in payout_line):  # all values are equal
            matched_value = payout_line[0]
            emoji = self.reel.get_emoji(matched_value)
            payout = self.reel.get_payout(matched_value)
            message = f"Three {emoji}s! You've been paid out {payout:,}× your wager!"
            payout = wager * payout

        elif payout_line.count("cherries") == 2:  # 2 cherries
            MULTIPLIER = 5
            message = f"Two {self.reel.get_emoji('cherries')}s! You've been paid out {MULTIPLIER:,}× your wager!"
            payout = wager * MULTIPLIER

        elif payout_line.count("cherries") == 1:  # 1 cherry
            MULTIPLIER = 2
            message = f"One {self.reel.get_emoji('cherries')}! You've been paid out {MULTIPLIER:,}× your wager!"
            payout = wager * MULTIPLIER

        else:  # no matches
            message = f"No matches! Better luck next time..."
            payout = 0
        return (message, payout)


    def format_output_for_message(self, slot_output):
        """Given the output of a slot machine play, format it in a human-readable manner before it is returned to the user."""
        values = [[self.reel.get_emoji(key) for key in row] for row in slot_output]
        rotated_values = [list(row) for row in zip(*values)]
        message = f"""
            {ky.EMPTY.value} {"".join(rotated_values[0])}
            {ky.RIGHT.value} {"".join(rotated_values[1])}
            {ky.EMPTY.value} {"".join(rotated_values[2])}
        """
        return message


    def play(self):
        """The main slot game mechanism. Runs through the logic of the slot game and returns an discord.Embed message that describes the results of the slot pull."""
        if not user_utils.is_registered(self.user):
            return bot_utils.create_error_response(message="You're not registered! Use `/register` first to participate in economy-related features.)")

        if not user_utils.can_afford(self.user, self.wager):
            return bot_utils.create_error_response(message=f"You can't afford that! Your balance is {user_utils.get_balance(user):,} {ky.CURRENCY.value}, but you tried to wager {self.wager:,} {ky.CURRENCY.value}.")

        reel = self.create_reel()
        slot_output = [self.pick_random_triplet_in_reel(reel) for i in range(3)]
        embed = discord.Embed(title="Slot Results:", description=self.format_output_for_message(slot_output))
        
        payout = self.determine_payout(slot_output, self.wager)
        payout_message = payout[0]
        payout_winnings = payout[1]
        new_balance = user_utils.get_balance(self.user) + payout_winnings - self.wager
        user_utils.set_balance(self.user, new_balance)

        payout_report = f"**New Balance:** {new_balance:,} {ky.CURRENCY.value}"
        if payout_winnings != 0:  # only report winnings if the user had actually won anything
            payout_report = f"**You've won:** {payout_winnings:,} {ky.CURRENCY.value}\n" + payout_report

        embed.add_field(name=payout_message, value=payout_report)
        return embed


class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    slots = app_commands.Group(name = "slots", description = "Ring-a-Ding-Ding!")
    
    @slots.command(name="payouts", description="Review the different kind of payouts available")
    async def review_payouts(self, interaction: discord.Interaction):
        reel = Reel()
        ordered_list = reel.get_keys(sort_keys=True)
        cherry_emoji = reel.get_emoji(ordered_list[0])
        payouts = [f"{ky.EMPTY.value*2}{cherry_emoji} Bet×2", f"{ky.EMPTY.value}{cherry_emoji*2} Bet×5"]
        for key in ordered_list:
            emoji, payout = (reel.get_emoji(key), reel.get_payout(key))
            payouts.append(f"{emoji*3} Bet×{payout}")
        message = "\n".join(payouts[:-1])  # omit the last, secret payout
        embed = discord.Embed(title="Slot Payouts", description=message)
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @slots.command(name="play", description="Gamble your money away!")
    @app_commands.describe(wager="The amount of money to wager (must be at least 100)")
    async def slots_command(self, interaction: discord.Interaction, wager: app_commands.Range[int, 100]):
        slot_game = SlotGame(interaction, wager)
        view = ReplayButton(slot_game)
        embed = slot_game.play()  # create new instance of a slot game
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Slots(bot))