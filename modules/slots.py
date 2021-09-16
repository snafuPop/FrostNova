import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids
import random
from modules.utils import user_json
from enum import Enum

class Reel(Enum):
  CHERRY = ":cherries:"
  BELL = ":bell:"
  STAR = ":eight_pointed_black_star:"
  SEVEN = ":seven:"
  LEMON = ":lemon:"
  GRAPE = ":grapes:"
  ORANGE = ":tangerine:"
  EMPTY = ":cyclone:"

class Slots(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.payouts = {
      # Reel.CHERRY: 2 (one cherry),
      # Reel.CHERRY: 5 (two cherries),
      Reel.CHERRY: 10,
      Reel.BELL: 10,
      Reel.STAR: 20,
      Reel.SEVEN: 30,
      Reel.LEMON: 40,
      Reel.GRAPE: 60,
      Reel.ORANGE: 100,
      Reel.EMPTY: 0
    }

  def get_payout(self, center_row):
    row = set(center_row)
    if len(row) == 1:
      return self.payouts[row.pop()]
    elif Reel.CHERRY in row:
      if len(row) == 2:
        return 5
      else:
        return 2
    else:
      return 0


  def generate_reel(self):
    reel = [[0, 0, 0],
            [0, 0, 0], 
            [0, 0, 0]]
    for row in range(0, 3):
      for col in range(0, 3):
        reel[col][row] = random.choice(list(Reel))
    return reel


  def beautify_reel(self, reel):
    reel_string = ""
    for row in range(0, 3):
      for col in range(0, 3):
        reel_string += reel[row][col].value + " "
      if row == 1:
        reel_string += ":arrow_left:"
      reel_string += "\n"
    return reel_string


  def create_slot_embed(self, user, bet):
    reel = self.generate_reel()
    center_row = reel[1]

    payout_mult = self.get_payout(center_row)
    payout_total = bet * payout_mult

    user_money = user_json.get_balance(user)
    user_money_after = user_money - bet + payout_total

    embed = discord.Embed(title = "", description = self.beautify_reel(reel))
    embed.set_author(name = "{}'s Slot Machine".format(user.name), icon_url = user.avatar_url)
    embed.add_field(name = "**Payout:**", value = "{:,} × **{}** = {:,} {}".format(bet, payout_mult, payout_total, user_json.get_currency_name()))
    embed.set_footer(text = "Balance: {:,} → {:,} {}".format(user_money, user_money_after, user_json.get_currency_name()))

    self.slot_payout(user, payout_total - bet)
    return embed

  def slot_payout(self, user, value):
    user_json.add_balance(user, value)
    user_json.add_slot_winnings(user, value)

  # plays slots
  @cog_ext.cog_slash(name = "slots", description = "Play some slots!", guild_ids = guild_ids,
    options = [create_option(
      name = "bet",
      description = "Amount of money to bet (must be at least 100 {}.".format(user_json.get_currency_name()),
      option_type = 4,
      required = True)])
  async def slots(self, ctx, bet: int = 0):
    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = ":no_entry: It looks like you aren't reigsted in the system, {}. Try `/register`.").format(ctx.author.mention)

    elif bet < 100:
      embed = discord.Embed(title = "", description = ":no_entry: You have to bet at least **100 {}**, {}.".format(user_json.get_currency_name(), ctx.author.mention))

    elif bet > user_json.get_balance(ctx.author):
      embed = discord.Embed(title = "", description = ":no_entry: You don't have that much, {}!".format(ctx.author.mention))
      embed.set_footer(text = "You have {:,} {}.".format(user_json.get_balance(ctx.author), user_json.get_currency_name()))

    else:
      embed = self.create_slot_embed(ctx.author, bet)

      buttons = [manage_components.create_button(style = ButtonStyle.green, label = "{:,}".format(bet), emoji = "🔁")]
      action_row = manage_components.create_actionrow(*buttons)
      
      await ctx.send(embed = embed, components = [action_row])

      while user_json.get_balance(ctx.author) >= bet:
        button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
        await button_ctx.edit_origin(embed = self.create_slot_embed(ctx.author, bet))

    await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Slots(bot))