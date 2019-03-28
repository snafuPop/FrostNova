import discord
from discord.ext import commands
from builtins import bot
import json
import random
import string
from enum import Enum
from modules.utils import perms

class CantDo(Exception):
  pass

class InvalidArgs(Exception):
  pass

# enum-type containing list of all possible symbols
class Slots(Enum):
  cherry = "\N{CHERRIES}"
  bell   = "\N{BELL}"
  money  = "\N{MONEY WITH WINGS}"
  seven  = "\N{MONEY BAG}"
  lemon  = "\N{LEMON}"
  grape  = "\N{GRAPES}"
  orange = "\N{TANGERINE}"
  gun    = "\N{PISTOL}"
  no_win = "\N{RADIO BUTTON}"

# class containing all possible payouts
class Payout:
  def __init__(self, bot):
    self.bot = bot
    self.payout_message = discord.Embed(title = "**Slot Payouts**")
    self.payout_message.add_field(name = "{gun.value} {gun.value} {gun.value}".format(**Slots.__dict__), value = "Bet \u00d7 200")
    self.payout_message.add_field(name = "{orange.value} {orange.value} {orange.value}".format(**Slots.__dict__), value = "Bet \u00d7 100", inline = True)
    self.payout_message.add_field(name = "{grape.value} {grape.value} {grape.value}".format(**Slots.__dict__), value = "Bet \u00d7 60")
    self.payout_message.add_field(name = "{lemon.value} {lemon.value} {lemon.value}".format(**Slots.__dict__), value = "Bet \u00d7 40", inline = True)
    self.payout_message.add_field(name = "{seven.value} {seven.value} {seven.value}".format(**Slots.__dict__), value = "Bet \u00d7 30")
    self.payout_message.add_field(name = "{money.value} {money.value} {money.value}".format(**Slots.__dict__), value = "Bet \u00d7 10", inline = True)
    self.payout_message.add_field(name = "{cherry.value} {cherry.value} {cherry.value}".format(**Slots.__dict__), value = "Bet \u00d7 10")
    self.payout_message.add_field(name = "{cherry.value} {cherry.value}".format(**Slots.__dict__), value = "Bet \u00d7 5", inline = True)
    self.payout_message.add_field(name = "{cherry.value}".format(**Slots.__dict__), value = "Bet \u00d7 2")

  def get_payouts(self):
    return self.payout_message

  @commands.command(pass_context = True, description = "Returns a list of possible payouts")
  async def payouts(self, ctx):
    await self.bot.send_message(ctx.message.author, embed = self.get_payouts())

class Economy:
  def __init__(self, bot):
    self.bot = bot
    self.name = "pennies"
    self.payday_amount = 500
    with open("modules/_data/users.json") as json_data:
      self.users = json.load(json_data)
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


  # updates the .json with new values and creates a back-up
  def update(self, user):
    with open("modules/_data/users.json", "w") as json_out:
      json.dump(user, json_out, indent = 2)


  # get a dict object of all possible payouts for slots
  def get_payout_dict(self):  
    return self.payout


  # returns the name of the currency
  def get_currency_name(self):
    return self.name


  # returns the payday value
  def get_payday(self):
    return self.payday_amount


  # checks if the user is registered within the system
  def is_registered(self, user):
    return user.id in self.users


  # returns the balance of a specified user
  def get_balance(self, user):
    return self.users[user.id]["balance"]


  # adds (or subtracts) credits to/from a user
  def add_balance(self, user, credits):
    self.users[user.id]["balance"] = self.get_balance(user) + credits
    self.update(self.users)


  # checks if the user can pay for a certain action
  def can_spend(self, user, cost):
    return self.get_balance(user) >= cost


  # checks through basic requirements for using economy actions
  # if everything is okay, we return the money value back
  async def can_do(self, user, money):
    if not self.is_registered(user):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(user.mention))
      await self.bot.say(embed = embed)
      raise CantDo

    # checks for strings as input
    money = self.__interpret_frac(user, money)
    
    # nothing particular happens -- should be handled by individual methods through a try-catch    
    if money == None:
      raise InvalidArgs

    # if money is a value less than or equal to 0
    elif money <= 0:
      embed = discord.Embed(title = "", description = "You need to spend more than 0 {}, {}.".format(self.get_currency_name(), user.mention))
      await self.bot.say(embed = embed)
      raise CantDo
    
    # if the money is more than the user can spend
    elif not self.can_spend(user, money):
      embed = discord.Embed(title = "", description = "You don't have enough {} for that, {}!".format(self.get_currency_name(), user.mention))
      await self.bot.say(embed = embed)
      raise CantDo

    return money


  # allows users to give fractional strings as arguments and interprets them into integer values
  def __interpret_frac(self, user, money):
    if money == None:
      return
    if money.isdigit():
      return int(money)
    if money == "all":
      return self.get_balance(user)
    if money == "half":
      return self.get_balance(user)//2
    if money == "fourth":
      return self.get_balance(user)//4
    if money == "tenth":
      return self.get_balance(user)//10
    return


  # registers an economy account with the bot
  @commands.command(pass_context = True, description = "Registers an account with the bot")
  async def register(self, ctx):
    if ctx.message.author.id in self.users:
      embed = discord.Embed(title = "", description = "You're already registered on my database, {}.".format(ctx.message.author.mention))
    else:
      user = {"username": ctx.message.author.name, "balance": 1000}
      self.users[ctx.message.author.id] = user
      self.update(self.users)
      embed = discord.Embed(title = "", description = "You're now registered on my database, {}!".format(ctx.message.author.mention))
    await self.bot.say(embed = embed)


  # pays out x credits to a user
  @commands.command(pass_context = True, description = "Gives some currency every so often")
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def payday(self, ctx):
    if self.is_registered(ctx.message.author):
      self.add_balance(ctx.message.author, self.get_payday())
      embed = discord.Embed(title = "", description = "Here's {} {}, {}.".format(self.get_payday(), self.get_currency_name(), ctx.message.author.mention), color = ctx.message.author.color)
    else:
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(ctx.message.author.mention))
    await self.bot.say(embed = embed)


  # cashes in a coupon
  @commands.command(pass_context = True, description = "Cashes in a coupon")
  async def coupon(self, ctx, *, coupon_code: str = None):

    # checks for null input
    if coupon_code == None:
      embed = discord.Embed(title = "", description = "You can cash in a coupon by using `!coupon <coupon code>`")
    else:

      # opening the list of coupons
      with open("modules/_data/coupons.json") as json_coupons:
        coupons = json.load(json_coupons)

      if coupon_code not in coupons:
        embed = discord.Embed(title = "", description = "It seems that coupon code is invalid, {}. Double check case sensitivity and make sure this coupon has not been claimed already.".format(ctx.message.author.mention))
      else:
        value = coupons.pop(coupon_code)
        self.add_balance(ctx.message.author, value)
        with open("modules/_data/coupons.json", "w") as json_out_coupon:
          json.dump(coupons, json_out_coupon, indent = 2)
        embed = discord.Embed(title = "", description = "Successfully cashed in coupon for {} {}, {}".format(value, self.get_currency_name(), ctx.message.author.mention), color = ctx.message.author.color)
    await self.bot.say(embed = embed)


  # generates a coupon that can be cashed in for currency
  @perms.is_owner()
  @commands.command(pass_context = True, description = "Generates a coupon")
  async def make_coupon(self, ctx, credits: int = 0):
    # checks for null input
    if credits <= 0:
      print("Invalid number of credits to be dispensed.")
    else:

      # opening the list of coupons
      with open("modules/_data/coupons.json") as json_coupons:
        coupons = json.load(json_coupons)

      # generating a random coupon code and makes sure it doesn't already exists
      random_string = string.ascii_letters + string.digits
      coupon_code = ""
      while (coupon_code == "") and (coupon_code not in coupons):
        for length in range(16):
          coupon_code = coupon_code + random.choice(random_string)
        coupon_code = '-'.join(coupon_code[i:i+4] for i in range(0, len(coupon_code), 4))

      # prints the coupon code in the command prompt
      print("Generated new coupon code: {}\nValued at {} {}\n".format(coupon_code, credits, self.get_currency_name()))

      # creates a dict entry for the coupon
      coupon = {coupon_code: credits}
      with open("modules/_data/coupons.json", "w") as json_out_coupon:
        json.dump(coupon, json_out_coupon, indent = 2)


  # transfers credits to another user
  @commands.command(pass_context = True, description = "Transfers currency to another user")
  async def transfer(self, ctx, recipient: discord.Member = None, money: int = 0):
    # checks if the user is trying to send currency to themselves
    if ctx.message.author == recipient:
      embed = discord.Embed(title = "", description = "You can't send {} to yourself, {}!".format(self.get_currency_name(), ctx.message.author.mention)) 
    try:
      money = await self.can_do(ctx.message.author, money)
    except InvalidArgs:
      embed = discord.Embed(title = "", description = "Send {} to another user with `!transfer <recipient> <number of {}>`".format(self.get_currency_name(), self.get_currency_name()))
    except CantDo:
      return
      
    # checks if the recipient is registered
    if not self.is_registered(recipient):
      embed = discord.Embed(title = "", description = "It looks like **{}** isn't registered in the system, {}".format(recipient.name, ctx.message.author.mention))
    
    else:
      self.add_balance(ctx.message.author, -money)
      self.add_balance(recipient, money)
      embed = discord.Embed(title = "", description = "{} sent {} {} to {}".format(ctx.message.author.mention, money, recipient.mention), color = ctx.message.author.color)
    await self.bot.say(embed = embed)


  # plays slots
  @commands.command(pass_context = True, aliases = ["slot"], description = "Play some slots!")
  async def slots(self, ctx, bid: str = None):
    try:
      bid = await self.can_do(ctx.message.author, bid)
    except InvalidArgs:
      embed = discord.Embed(title = "", description = "You can play slots by with `!slots <bid greater than 0>`.")
      await self.bot.say(embed = embed)
      return
    except CantDo:
      return

    # generating reels
    reel = []
    reel_list = list(Slots)
    for row in range(3):
      # to make the slots realistic, each column contains 3 contiguous icons, rather than 3 completely randomly popped ones
      rand_choice = random.randint(0,len(list(Slots))-1)
      reel_row = []
      reel_row.append(reel_list[(rand_choice-1)%len(reel_list)].value)
      reel_row.append(reel_list[rand_choice].value)
      reel_row.append(reel_list[(rand_choice+1)%len(reel_list)].value)
      reel_row.append(reel_list[rand_choice].name)
      reel.append(reel_row)

    # starting to create the embed message
    embed = discord.Embed(title = "", description = ctx.message.author.mention, color = ctx.message.author.color)
    embed.add_field(name = "\u3164", value = "{} {} {}\n{} {} {} ⬅\n{} {} {}".format(reel[0][0], reel[1][0], reel[2][0], reel[0][1], reel[1][1], reel[2][1], reel[0][2], reel[1][2], reel[2][2]))

    # grabbing initial information for the final embed message
    initial_balance = self.get_balance(ctx.message.author)

    # checking for a payout
    reel_key = [reel[0][3], reel[1][3], reel[2][3]]
    if reel_key[0] == reel_key[1] == reel_key[2]:
      payout = self.__payouts(reel_key[0])
    elif (reel_key[0] == reel_key[1] and reel_key[0] == "cherry") or (reel_key[1] == reel_key[2] and reel_key[1] == "cherry"):
      payout = self.__payouts("2cherry")
    elif reel_key[0] == "cherry" or reel_key[1] == "cherry" or reel_key[2] == "cherry":
      payout = self.__payouts("1cherry")
    else:
      payout = self.__payouts("none")

    # paying out
    final_payout = bid*payout["payout"]
    self.add_balance(ctx.message.author, -bid)
    self.add_balance(ctx.message.author, final_payout)
    
    # adding payout to embed
    embed.add_field(name = "Payout:", value = "{}\n{} ⮕ {} {}".format(payout["output"], initial_balance, self.get_balance(ctx.message.author), self.get_currency_name()), inline = False)
    embed.set_footer(text = "Your bet of {} {} became {}.".format(bid, self.get_currency_name(), final_payout))
    await self.bot.say(embed = embed)


  # helper method for slots -- quickly pulls information from the payouts dictionary
  def __payouts(self, key):
    return self.payout[key]

  @commands.command(pass_context = True, description = "Attempt to rob another user")
  async def rob(self, ctx, user: discord.Member = None, money: str = None):
    pass



  # error handler that returns an embed message with the remaining time left on a particular command
  #@slots.error
  #@payday.error
  #async def cd_error(self, error, ctx):
  #  if isinstance(error, commands.CommandOnCooldown):
  #    time_left = error.retry_after
  #    time_unit = "seconds"
  #    if time_left >= 60:
  #      time_left = time_left//60
  #      time_unit = "minutes"
  #   await self.bot.say(embed = discord.Embed(title = "", description = "This command is still on cooldown, {}. Try again in {:.0f} {}.".format(ctx.message.author.mention, time_left, time_unit)))



def setup(bot):
  bot.add_cog(Economy(bot))
  bot.add_cog(Payout(bot))