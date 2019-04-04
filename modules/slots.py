import discord
from discord.ext import commands
from builtins import bot
import random
from enum import Enum
from modules.utils import user_json

# enum-type containing list of all possible symbols
class Reel_Types(Enum):
  cherry = "\N{CHERRIES}"
  bell   = "\N{BELL}"
  money  = "\N{MONEY WITH WINGS}"
  seven  = "\N{MONEY BAG}"
  lemon  = "\N{LEMON}"
  grape  = "\N{GRAPES}"
  orange = "\N{TANGERINE}"
  gun    = "\N{PISTOL}"
  no_win = "\N{RADIO BUTTON}"

class Slots(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.payout = {
      "gun": {
        "payout": 200,
        "output": "You found Ranger Rod! Your bet was multiplied by 200."
      },
      "orange": {
        "payout": 100,
        "output": "Three oranges! Your bet was multiplied by 100."
      },
      "grape": {
        "payout": 60,
        "output": "Three grapes! Your bet was multiplied by 60."
      },
      "lemon": {
        "payout": 40,
        "output": "Three lemons! Your bet was multiplied by 40."
      },
      "seven": {
        "payout": 30,
        "output": "Three moneybags! Your bet was multiplied by 30."
      },
      "money": {
        "payout": 20,
        "output": "Three dollar bills! Your bet was multiplied by 10."
      },
      "bell": {
        "payout": 10,
        "output": "Three bells! Your bet was mutliplied by 10."
      },
      "3cherry": {
        "payout": 10,
        "output": "Three cherries! Your bet was multiplied by 10."
      },
      "2cherry": {
        "payout": 5,
        "output": "Two cherries! Your bet was multiplied by 5."
      },
      "1cherry": {
        "payout": 2,
        "output": "One cherry! Your bet was multiplied by 2."
      },
      "none": {
        "payout": 0,
        "output": "No matches! You lost your bet."
      }
    }


  # plays slots
  @commands.command(aliases = ["slot"], description = "Play some slots!")
  async def slots(self, ctx, bid: str = None):
    try:
      bid = await user_json.can_do(ctx, ctx.author, bid)
    except:
      embed = discord.Embed(title = "", description = "You can play slots by with `!slots <bid greater than 0>`.")
      await ctx.send(embed = embed)
      return

    if bid < 100:
      await ctx.send(embed = discord.Embed(title = "", description = "You have to bet at least **100 {}**, {}.".format(user_json.get_currency_name(), ctx.author.mention)))
      return

    # generating reels
    reel = []
    reel_list = list(Reel_Types)
    for row in range(3):
      # to make the slots realistic, each column contains 3 contiguous icons, rather than 3 completely randomly popped ones
      rand_choice = random.randint(0,len(list(Reel_Types))-1)
      reel_row = []
      reel_row.append(reel_list[(rand_choice-1)%len(reel_list)].value)
      reel_row.append(reel_list[rand_choice].value)
      reel_row.append(reel_list[(rand_choice+1)%len(reel_list)].value)
      reel_row.append(reel_list[rand_choice].name)
      reel.append(reel_row)

    # starting to create the embed message
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)
    embed.add_field(name = "\u3164", value = "{} {} {}\n{} {} {} ⬅\n{} {} {}".format(reel[0][0], reel[1][0], reel[2][0], reel[0][1], reel[1][1], reel[2][1], reel[0][2], reel[1][2], reel[2][2]))

    # grabbing initial information for the final embed message
    initial_balance = user_json.get_balance(ctx.message.author)

    # checking for a payout
    reel_key = [reel[0][3], reel[1][3], reel[2][3]]
    if reel_key[0] == reel_key[1] == reel_key[2]:
      payout = self.payout[str(reel_key[0])]
    elif (reel_key[0] == reel_key[1] and reel_key[0] == "cherry") or (reel_key[1] == reel_key[2] and reel_key[1] == "cherry"):
      payout = self.payout["2cherry"]
    elif reel_key[0] == "cherry" or reel_key[1] == "cherry" or reel_key[2] == "cherry":
      payout = self.payout["1cherry"]
    else:
      payout = self.payout["none"]

    # paying out
    final_payout = bid*payout["payout"]
    user_json.add_balance(ctx.author, -bid)
    user_json.add_balance(ctx.author, final_payout)

    # updating stats
    users_dict = user_json.get_users()
    users_dict[str(ctx.author.id)]["slot_winnings"] = users_dict[str(ctx.author.id)]["slot_winnings"] + (final_payout-bid)
    user_json.update(users_dict)

    # adding payout to embed
    embed.add_field(name = "Payout:", value = "{}\n{:,} ⮕ {:,} {}".format(payout["output"], initial_balance, user_json.get_balance(ctx.author), user_json.get_currency_name()), inline = False)
    embed.set_footer(text = "Your bet of {:,} {} became {:,}.".format(bid, user_json.get_currency_name(), final_payout))
    await ctx.send(embed = embed)


  @commands.command(description = "Returns a list of possible payouts")
  async def payouts(self, ctx):
    payout_message = discord.Embed(title = "**Slot Payouts**")
    payout_message.add_field(name = "{gun.value} {gun.value} {gun.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 200")
    payout_message.add_field(name = "{orange.value} {orange.value} {orange.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 100", inline = True)
    payout_message.add_field(name = "{grape.value} {grape.value} {grape.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 60")
    payout_message.add_field(name = "{lemon.value} {lemon.value} {lemon.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 40", inline = True)
    payout_message.add_field(name = "{seven.value} {seven.value} {seven.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 30")
    payout_message.add_field(name = "{money.value} {money.value} {money.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 10", inline = True)
    payout_message.add_field(name = "{cherry.value} {cherry.value} {cherry.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 10")
    payout_message.add_field(name = "{cherry.value} {cherry.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 5", inline = True)
    payout_message.add_field(name = "{cherry.value}".format(**Reel_Types.__dict__), value = "Bet \u00d7 2")
    await ctx.author.send(embed = payout_message)

def setup(bot):
  bot.add_cog(Slots(bot))