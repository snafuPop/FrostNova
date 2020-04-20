import discord
from discord.ext import commands
from builtins import bot
import random
import math
from modules.utils import user_json

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


# ----------------------------------------------------------------------------------------------------
# owner commands
# ----------------------------------------------------------------------------------------------------

  # adds new keys to all users
  @commands.is_owner()
  @commands.command(hidden = True, description = "Adds a key to the user dictionary.")
  async def add_dict(self, ctx, *, new_key: str = None):
    if new_key is None:
      await ctx.send(embed = discord.Embed(title = "", description = "Invalid key"))
      return
    logger = 0
    user_dict = user_json.get_users()
    for user_id in user_dict:
      user_key = user_dict[user_id]
      if new_key not in user_key.keys():
        user_key[new_key] = 0
        logger += 1
    user_json.update(user_dict)
    await ctx.send(embed = discord.Embed(title = "", description = "**{}** added to **{}** users".format(new_key, logger)))

  # remove key from all users
  @commands.is_owner()
  @commands.command(hidden = True, description = "Removes a key from the user dictionary.")
  async def remove_dict(self, ctx, *, dict_key: str = None):
    if dict_key is None:
      await ctx.send(embed = discord.Embed(title = "", description = "Invalid key"))
      return
    logger = 0
    user_dict = user_json.get_users()
    for user_id in user_dict:
      if user_dict[user_id].pop(dict_key, None) is not None:
        logger += 1
    user_json.update(user_dict)
    await ctx.send(embed = discord.Embed(title = "", description = "**{}** removed from **{}** users".format(dict_key, logger)))


  # sets a new balance to a user
  @commands.is_owner()
  @commands.command(hidden = True, description = "Sets the currency of a user.")
  async def set_balance(self, ctx, user: discord.Member = None, credits: int = -1):
    if user is None:
      embed = discord.Embed(title = "", description = "Invalid user")
    if credits < 0:
      embed = discord.Embed(title = "", description = "Invalid balance")
    else:
      user_dict = user_json.get_users()
      user_dict[str(user.id)]["balance"] = credits
      user_json.update(user_dict)
      embed = discord.Embed(title = "", description = "Successfully set {}'s balance to {}.".format(user.mention, credits))
    await ctx.send(embed = embed)

# ----------------------------------------------------------------------------------------------------
# regular commands
# ----------------------------------------------------------------------------------------------------

  # registers an economy account with the bot
  @commands.command(description = "Registers an account with the bot.")
  async def register(self, ctx):
    user_dict = user_json.get_users()
    if str(ctx.author.id) in user_dict:
      embed = discord.Embed(title = "", description = "You're already registered on my database, {}.".format(ctx.message.author.mention))
    else:
      user = {"username": ctx.author.name,
              "balance": 1000,
              "slot_winnings": 0,
              "stolen_money": 0,
              "text_posts": 0,
              "inventory": [],
              "level": 1,
              "exp": 0,
              "raids": 0,
              "loot_earnings": 0,
              "item_level": 0}
      user_dict[str(ctx.author.id)] = user
      user_json.update(user_dict)
      embed = discord.Embed(title = "", description = "You're now registered on my database, {}!".format(ctx.message.author.mention))
    await ctx.send(embed = embed)


  # transfers credits to another user
  @commands.command(description = "Transfers currency to another user.")
  async def transfer(self, ctx, recipient: discord.Member = None, money: str = None):
    # checks if the user is trying to send currency to themselves
    if ctx.author == recipient:
      embed = discord.Embed(title = "", description = "You can't send {} to yourself, {}!".format(self.get_currency_name(), ctx.author.mention))
    try:
      money = await user_json.can_do(ctx, ctx.author, money)
    except:
      embed = discord.Embed(title = "", description = "Send {} to another user with `!transfer <recipient> <number of {}>`".format(user_json.get_currency_name(), user_json.get_currency_name()))
      await ctx.send(embed = embed)
      return

    # checks if the recipient is registered
    if not user_json.is_registered(recipient):
      embed = discord.Embed(title = "", description = "It looks like **{}** isn't registered in the system, {}".format(recipient.name, ctx.author.mention))

    else:
      user_json.add_balance(ctx.author, -money)
      user_json.add_balance(recipient, money)
      embed = discord.Embed(title = "", description = "{} sent {:,} {} to {}".format(ctx.author.mention, money, user_json.get_currency_name(), recipient.mention), color = ctx.author.color)
    await ctx.send(embed = embed)


  # attempts to rob a user
  @commands.command(description = "Attempt to rob another user.", cooldown_after_parsing = True)
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def rob(self, ctx, user: discord.Member = None, money: str = None):
    # checks if the user is trying to rob themselves
    money = user_json.interpret_frac(user, money)
    if money == None or user is None:
      embed = discord.Embed(title = "", description = "Rob another user with `{}rob <user> <number of {}>`".format(ctx.prefix, user_json.get_currency_name(), user_json.get_currency_name()))
      ctx.command.reset_cooldown(ctx)
    elif ctx.author == user:
      embed = discord.Embed(title = "", description = "You can't rob yourself, {}!".format(ctx.author.mention))
      ctx.command.reset_cooldown(ctx)
    elif not user_json.is_registered(user):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(user.mention))
      ctx.command.reset_cooldown(ctx)
    elif money <= 0:
      embed = discord.Embed(title = "", description = "You need to steal more than 0 {}, {}.".format(user_json.get_currency_name(), user.mention))
      ctx.command.reset_cooldown(ctx)
    elif not user_json.is_registered(user):
      embed = discord.Embed(title = "", description = "It looks like **{}** isn't registered in the system, {}".format(user.name, ctx.author.mention))
      ctx.command.reset_cooldown(ctx)
    elif not user_json.can_spend(user, money):
      embed = discord.Embed(title = "", description = "**{}** doesn't have that much currency (They have {} {})!".format(user.name, user_json.get_balance(user), user_json.get_currency_name()))
      ctx.command.reset_cooldown(ctx)
    else:
      # makes it so that the more money you are trying to steal, the harder it is to be successful
      success_rate = int(math.ceil(100-((money**1.3874)/user_json.get_balance(user))*.98))

      # makes it so that it's never guaranteed to work
      if success_rate >= 90:
        success_rate = 90

      # the minimum success rate is 1%
      if success_rate <= 0:
        success_rate = 1

      # getting initial data
      initial_money_robber = user_json.get_balance(ctx.author)
      initial_money_target = user_json.get_balance(user)
      rand_rate = random.randint(1,100)

      # successful robbery -- user is paid out the amount they specified from the target
      if success_rate >= rand_rate:
        embed = discord.Embed(title = "", description = "Robbery successful! You stole **{:,} {}** from {}!".format(money, user_json.get_currency_name(), user.mention), color = ctx.author.color)

        user_json.add_balance(ctx.author, money)
        user_json.add_balance(user, -money)

        embed.add_field(name = ctx.author.name, value = "{:,} ⮕ {:,} {}".format(initial_money_robber, user_json.get_balance(ctx.author), user_json.get_currency_name()), inline = False)
        embed.add_field(name = user.name, value = "{:,} ⮕ {:,} {}".format(initial_money_target, user_json.get_balance(user), user_json.get_currency_name()), inline = False)

        # updating stats
        user_dict = user_json.get_users()
        user_dict[str(ctx.author.id)]["stolen_money"] = user_dict[str(ctx.author.id)]["stolen_money"] + (money)
        user_json.update(user_dict)

      # unsuccessful robbery -- user must pay a random percentage of their money equal to the inverse of the success rate
      else:
        loss = int((user_json.get_balance(ctx.author)*((100-success_rate)/100)))
        user_json.add_balance(ctx.author, -loss)
        embed = discord.Embed(title = "", description = "You were caught trying to steal from {}! You paid out **{:,} {}** in legal fees".format(user.name, loss, user_json.get_currency_name()), color = ctx.author.color)
        embed.add_field(name = ctx.author.name, value = "{:,} ⮕ {:,} {}".format(initial_money_robber, user_json.get_balance(ctx.author), user_json.get_currency_name()))
      embed.set_footer(text = "You had a {}% success rate".format(success_rate))
    await ctx.send(embed = embed)


  # error handler that returns an embed message with the remaining time left on a particular command
  @rob.error
  async def cd_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      time_left = int(error.retry_after)
      if time_left >= 3600:
        time_left = time_left//3600
        time_unit = "hour(s)"
      elif time_left >= 60:
        time_left = time_left//60
        time_unit = "minute(s)"
      else:
        time_unit = "second(s)"
      await ctx.send(embed = discord.Embed(title = "", description = "This command is still on cooldown, {}. Try again in {:.0f} {}.".format(ctx.author.mention, time_left, time_unit)))
    else:
      raise error

def setup(bot):
  bot.add_cog(Economy(bot))