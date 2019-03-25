import discord
from discord.ext import commands
from builtins import bot
import json
import random
import string
from modules.utils import perms

class Economy:
  def __init__(self, bot):
    self.bot = bot
    self.name = "pennies"
    with open("modules/_data/users.json") as json_data:
      self.users = json.load(json_data)

  # updates the .json with new values
  def update(self, user):
    with open("modules/_data/users.json", "w") as json_out:
      json.dump(user, json_out, indent = 2)

  # returns the name of the currency
  def get_currency_name(self):
    return self.name

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
    return self.get_balance(user) > cost

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
  async def transfer(self, ctx, recipient: discord.Member = None, credits: int = 0):
    
    # checks if the user is trying to send currency to themselves
    if ctx.message.author == recipient:
      embed = discord.Embed(title = "", description = "You can't send {} to yourself, {}!".format(self.get_currency_name(), ctx.message.author.mention)) 

    # checks if the recipient is a user
    elif recipient is None:
      embed = discord.Embed(title = "", description = "Send {} to another user with `!transfer <recipient> <number of credits>".format(self.get_currency_name()))
    
    # checks if the user is registered
    elif not self.is_registered(ctx.message.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(ctx.message.author.mention))
    
    # checks if the recipient is registered
    elif not self.is_registered(recipient):
      embed = discord.Embed(title = "", description = "It looks like **{}** isn't registered in the system, {}".format(recipient.name, ctx.message.author.mention))
    
    # checks if the amount of currency to be sent is an int and is greater than 0
    elif type(credits) is not int or credits <= 0:
      embed = discord.Embed(title = "", description = "You must send at least 1 {}, {}".format(self.get_currency_name(), ctx.message.author.mention))
    
    # checks if the user has enough currency to send
    elif not self.can_spend(ctx.message.author, credits):
      embed = discord.Embed(title = "", description = "You don't have enough {} for that, {}!".format(self.get_currency_name(), ctx.message.author.mention))
    
    else:
      self.add_balance(ctx.message.author, -credits)
      self.add_balance(recipient, credits)
      embed = discord.Embed(title = "", description = "{} sent {} {} to {}".format(ctx.message.author.mention, credits, recipient.mention), color = ctx.message.author.color)
    await self.bot.say(embed = embed)

def setup(bot):
  bot.add_cog(Economy(bot))