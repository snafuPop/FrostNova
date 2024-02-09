import discord
from discord import app_commands
from discord.ext import commands
from cogs.utils.keywords import Keyword as ky
import cogs.utils.user_utils as user_utils
from random import randint, shuffle
from typing import Optional
from enum import Enum


class Reel(Enum):
    CHERRY = ":cherries:"
    BELL = ":bell:"
    DIAMOND = ":diamond_shape_with_a_dot_inside:"
    SEVEN = ":seven:"
    LEMON = ":lemon:"
    GRAPE = ":grapes:"
    ORANGE = ":tangerine:"
    SECRET = "<a:w_:1205606672970686545>"
    

class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def get_payouts(self):
        '''Returns a dictionary of payouts, where the key is the matched symbol and its value is the bet multiplier.'''
        return {
            Reel.CHERRY: 10,
            Reel.BELL: 10,
            Reel.DIAMOND: 20,
            Reel.SEVEN: 30,
            Reel.LEMON: 40,
            Reel.GRAPE: 60,
            Reel.ORANGE: 100,
            Reel.SECRET: 5000,
        }

    def is_not_registered_message(self, user):
        '''Returns an embed message intended for interactions that cannot be performed because the designated user is not registered.'''
        return self.bot.create_error_response(message=f"{user.name} is not registered! Use `/register` first to participate in economy-related features!")

    
    slots = app_commands.Group(name = "slots", description = "Ring-a-Ding-Ding!")
    
    @slots.command(name="payouts", description="Review the different kind of payouts available")
    async def review_payouts(self, interaction: discord.Interaction):
        payouts = self.get_payouts()
        message = f"""
            {ky.EMPTY.value*2}{Reel.CHERRY.value} Bet×2
            {ky.EMPTY.value}{Reel.CHERRY.value*2} Bet×5
            {Reel.CHERRY.value*3} Bet×{payouts[Reel.CHERRY]}
            {Reel.BELL.value*3} Bet×{payouts[Reel.BELL]}
            {Reel.DIAMOND.value*3} Bet×{payouts[Reel.DIAMOND]}
            {Reel.SEVEN.value*3} Bet×{payouts[Reel.SEVEN]}
            {Reel.LEMON.value*3} Bet×{payouts[Reel.LEMON]}
            {Reel.GRAPE.value*3} Bet×{payouts[Reel.GRAPE]}
            {Reel.ORANGE.value*3} Bet×{payouts[Reel.ORANGE]}
        """
        embed = discord.Embed(title="Slot Payouts", description=message)
        await interaction.response.send_message(embed=embed, ephemeral=True)


    def create_reel(self):
        '''Rather than randomly selecting a symbol, generate an ordered list of random symbols,  then pick a random symbol from that list.
        This simulates a phyhsical reel, in which symbols are at a fixed location.'''
        reel = [Reel.CHERRY]*20 + [Reel.BELL]*30 + [Reel.DIAMOND]*25 + [Reel.SEVEN]*20 + [Reel.LEMON]*12 + [Reel.GRAPE]*8 + [Reel.ORANGE]*4 + [Reel.SECRET] * 1
        shuffle(reel)
        return reel
    
    
    def pick_random_triplet_in_reel(self, reel):
        '''Picks a random triplet on the reel, circularly. The 0th index represents the top of the reel, and the 2nd index represents the
        bottom.'''
        index = randint(0, len(reel) - 1)
        return [reel[(index - 1) % len(reel)], reel[index], reel[(index + 1) % len(reel)]]
    
    
    def format_output_for_message(self, slot_output):
        '''Given the output of a slot machine play, format it in a human-readable manner before it is returned to the user.'''
        values = [[enum.value for enum in row] for row in slot_output]
        rotated_values = [list(row) for row in zip(*values)]
        message = f"""
            {ky.EMPTY.value} {"".join(rotated_values[0])}
            {ky.RIGHT.value} {"".join(rotated_values[1])}
            {ky.EMPTY.value} {"".join(rotated_values[2])}
        """
        return message
    
    
    def determine_payout(self, slot_output, wager):
        '''Given the output of a slot machine play, determine the payout. This is returned as a tuple
        (payout message, amount to be paid out).'''
        payouts = self.get_payouts()
        payout_line = [slot_output[0][1], slot_output[1][1], slot_output[2][1]]
        if all(value == payout_line[0] for value in payout_line):  # all values are equal
            matched_value = payout_line[0]
            message = f"Three {matched_value.value}s! You've been paid out {payouts[matched_value]:,}× your wager!"
            payout = wager * payouts[matched_value]
        elif payout_line.count(Reel.CHERRY) == 2:  # 2 cherries
            MULTIPLIER = 5
            message = f"Two {Reel.CHERRY.value}s! You've been paid out {MULTIPLIER:,}× your wager!"
            payout = wager * MULTIPLIER
        elif payout_line.count(Reel.CHERRY) == 1:  # 1 cherry
            MULTIPLIER = 2
            message = f"One {Reel.CHERRY.value}! You've been paid out {MULTIPLIER:,}× your wager!"
            payout = wager * MULTIPLIER
        else:  # no matches
            message = f"No matches! Better luck next time..."
            payout = 0
        return (message, payout)


    @slots.command(name="play", description="Gamble your money away!")
    @app_commands.describe(wager="The amount of money to wager (must be at least 100)")
    async def slots_play(self, interaction: discord.Interaction, wager: app_commands.Range[int, 100]):
        if not user_utils.is_registered(interaction.user):
            await interaction.response.send_message(embed=self.is_not_registered_message(interaction.user), ephemeral=True)
            return
        
        if not user_utils.can_afford(interaction.user, wager):
            message = f"You can't afford that! Your balance is {user_utils.get_balance(interaction.user):,} {ky.CURRENCY.value}, but you tried to wager {wager:,} {ky.CURRENCY.value}."
            await interaction.response.send_message(embed=self.bot.create_error_response(message=message), ephemeral=True)
            return

        reel = self.create_reel()
        slot_output = [self.pick_random_triplet_in_reel(reel) for i in range(3)]
        embed = discord.Embed(title="Slot Results:", description=self.format_output_for_message(slot_output))
        
        payout = self.determine_payout(slot_output, wager)
        payout_message = payout[0]
        payout_winnings = payout[1]
        new_balance = user_utils.get_balance(interaction.user) + payout_winnings - wager
        user_utils.set_balance(interaction.user, new_balance)

        payout_report = f"**New Balance:** {new_balance:,} {ky.CURRENCY.value}"
        if payout_winnings != 0:  # only report winnings if the user had actually won anything
            payout_report = f"**You've won:** {payout_winnings:,} {ky.CURRENCY.value}\n" + payout_report

        embed.add_field(name=payout_message, value=payout_report)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Slots(bot))