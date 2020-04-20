import discord
from discord.ext import commands
from builtins import bot
import random
from modules.utils import user_json

class Slots(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.reel_strip = ["none", "grape", "bell", "lemon", "cherry", "none", "money", "seven", "none", "cherry", "lemon", "none", "orange", "bell", "seven", "none", "gun", "none", "cherry", "money"]
    self.payout = {
      "gun": {
        "payout": 200,
        "icon": "\N{PISTOL}",
        "output": "You found Ranger Rod! Your bet was multiplied by 200."
      },
      "orange": {
        "payout": 100,
        "icon": "\N{TANGERINE}",
        "output": "Three oranges! Your bet was multiplied by 100."
      },
      "grape": {
        "payout": 60,
        "icon": "\N{GRAPES}",
        "output": "Three grapes! Your bet was multiplied by 60."
      },
      "lemon": {
        "payout": 40,
        "icon": "\N{LEMON}",
        "output": "Three lemons! Your bet was multiplied by 40."
      },
      "seven": {
        "payout": 30,
        "icon": "\N{MONEY BAG}",
        "output": "Three moneybags! Your bet was multiplied by 30."
      },
      "money": {
        "payout": 20,
        "icon": "\N{MONEY WITH WINGS}",
        "output": "Three dollar bills! Your bet was multiplied by 10."
      },
      "bell": {
        "payout": 10,
        "icon": "\N{BELL}",
        "output": "Three bells! Your bet was mutliplied by 10."
      },
      "3cherry": {
        "payout": 10,
        "icon": "\N{CHERRIES}",
        "output": "Three cherries! Your bet was multiplied by 10."
      },
      "2cherry": {
        "payout": 5,
        "icon": "\N{CHERRIES}",
        "output": "Two cherries! Your bet was multiplied by 5."
      },
      "1cherry": {
        "payout": 2,
        "icon": "\N{CHERRIES}",
        "output": "One cherry! Your bet was multiplied by 2."
      },
      "cherry": {
        "payout": 2,
        "icon": "\N{CHERRIES}",
        "output": "One cherry! Your bet was multiplied by 2."
      },
      "none": {
        "payout": 0,
        "icon": "\N{RADIO BUTTON}",
        "output": "No matches! You lost your bet."
      }
    }


  def get_reel_column(self):
    reel_length = len(self.reel_strip)
    rand_choice = random.randint(0, reel_length-1)
    reel_col = []
    reel_col.append(self.reel_strip[(rand_choice-1)%reel_length])
    reel_col.append(self.reel_strip[rand_choice])
    reel_col.append(self.reel_strip[(rand_choice+1)%reel_length])
    return reel_col

  def get_icon(self, key):
    return self.payout[key]["icon"]

  def get_payout(self, key):
    return self.payout[key]["payout"]

  # plays slots
  @commands.command(aliases = ["slot"], description = "Play some slots!")
  async def slots(self, ctx, bid: str = None):
    try:
      bid = await user_json.can_do(ctx, ctx.author, bid)
    except:
      embed = discord.Embed(title = "", description = "You can play slots by with `{}slots <bid greater than 0>`, {}.".format(ctx.prefix, ctx.author.mention))
      await ctx.send(embed = embed)
      return

    if bid < 100:
      await ctx.send(embed = discord.Embed(title = "", description = "You have to bet at least **100 {}**, {}.".format(user_json.get_currency_name(), ctx.author.mention)))
      return

    # generating reels
    reel = []
    for row in range(0,3):
      reel.append(self.get_reel_column())

    # starting to create the embed message
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)

    payout_msg = ""
    for i in range(0,3):
      for j in range(0,3):
        payout_msg += "{} ".format(self.get_icon(reel[j][i]))
      if i == 1: payout_msg += "⬅"
      payout_msg += "\n"
    embed.add_field(name = "\u3164", value = payout_msg)

    # grabbing initial information for the final embed message
    initial_balance = user_json.get_balance(ctx.message.author)

    # checking for a payout
    reel_key = [reel[0][1], reel[1][1], reel[2][1]]
    if (reel_key[0] == reel_key[1] == reel_key[2]) and reel_key[0] != "none":
      payout = self.payout["3cherry"] if reel_key[0] == "cherry" else self.payout[reel_key[0]]
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
    for key in ["gun", "orange", "grape", "lemon", "seven", "money", "bell"]:
      payout_message.add_field(name = "{0} {0} {0}".format(self.get_icon(key)), value = "Bet \u00d7 {}".format(self.get_payout(key)), inline = True)
    payout_message.add_field(name = "{0} {0} {0}".format(self.get_icon("cherry")), value = "Bet \u00d7 {}".format(self.get_payout("3cherry")), inline = True)
    payout_message.add_field(name = "{0} {0}".format(self.get_icon("cherry")), value = "Bet \u00d7 {}".format(self.get_payout("2cherry")), inline = True)
    payout_message.add_field(name = "{0}".format(self.get_icon("cherry")), value = "Bet \u00d7 {}".format(self.get_payout("1cherry")), inline = True)
    await ctx.author.send(embed = payout_message)

def setup(bot):
  bot.add_cog(Slots(bot))