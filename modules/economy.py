import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids
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
  @cog_ext.cog_subcommand(base = "dict", name = "add", description = "⛔ Adds a key to all users.",  
    options = [create_option(
      name = "key",
      description = "Key to be added.",
      option_type = 3,
      required = True),
    create_option(
      name = "value",
      description = "Value to be added (optional). Must be an integer and defaults to 0.",
      option_type = 4,
      required = False)
    ])
  async def add_dict(self, ctx, new_key: str = None, new_val: int = 0):
    logger = 0
    user_dict = user_json.get_users()
    for user_id in user_dict:
      user_key = user_dict[user_id]
      if new_key not in user_key.keys():
        user_key[new_key] = 0
        logger += 1
    user_json.update(user_dict)

    embed = discord.Embed(title = "Success!", description = "<{}, {}> added to **{}** users.".format(new_key, str(new_val), logger))
    await ctx.send(embed = embed)

  # remove key from all users
  @commands.is_owner()
  @cog_ext.cog_subcommand(base = "dict", name = "delete", description = "⛔ Removes a key from all users.", 
    options = [create_option(
      name = "key",
      description = "Key to be removed.",
      option_type = 3,
      required = True,
      choices = [create_choice(
        name = key_name,
        value = key_name)
      for key_name in user_json.get_keys()])])
  async def remove_dict(self, ctx, *, dict_key: str = None):
    logger = 0
    user_dict = user_json.get_users()
    for user_id in user_dict:
      if user_dict[user_id].pop(dict_key, None) is not None:
        logger += 1
    user_json.update(user_dict)
    await ctx.send(embed = discord.Embed(title = "Success!", description = "<{}> removed from **{}** users".format(dict_key, logger)))



  # sets a new balance to a user
  @commands.is_owner()
  @cog_ext.cog_subcommand(base = "balance", name = "set", description = "⛔ Sets a user's balance to a given value.", 
    options = [create_option(
      name = "user",
      description = "The name of a user.",
      option_type = 6,
      required = True),
    create_option(
      name = "credits",
      description = "Money value.",
      option_type = 4,
      required = True)])
  async def set_balance(self, ctx, user: discord.Member = None, credits: int = 0):
    user_dict = user_json.get_users()
    user_dict[str(user.id)]["balance"] = credits
    user_json.update(user_dict)
    embed = discord.Embed(title = "", description = "Successfully set {}'s balance to {:,}.".format(user.mention, credits))
    await ctx.send(embed = embed)


  @commands.is_owner()
  @cog_ext.cog_subcommand(base = "balance", name = "add", description = "⛔ Adds a given value to a user's balance.", 
    options = [create_option(
      name = "user",
      description = "The name of a user.",
      option_type = 6,
      required = True),
    create_option(
      name = "credits",
      description = "Money value.",
      option_type = 4,
      required = True)])
  async def add_balance(self, ctx, user: discord.Member = None, credits: int = 0):
    user_json.add_balance(user, credits)
    embed = discord.Embed(title = "", description = "Successfully added {:,} to {}'s balance.".format(credits, user.mention))
    await ctx.send(embed = embed)


  @commands.is_owner()
  @cog_ext.cog_subcommand(base = "balance", name = "subtract", description = "⛔ Subtracts a given value to a user's balance.", 
    options = [create_option(
      name = "user",
      description = "The name of a user.",
      option_type = 6,
      required = True),
    create_option(
      name = "credits",
      description = "Money value.",
      option_type = 4,
      required = True)])
  async def subtract_balance(self, ctx, user: discord.Member = None, credits: int = 0):
    user_json.add_balance(user, -credits)
    embed = discord.Embed(title = "", description = "Successfully added {:,} to {}'s balance.".format(credits, user.mention))
    await ctx.send(embed = embed)

# ----------------------------------------------------------------------------------------------------
# regular commands
# ----------------------------------------------------------------------------------------------------

  # registers an economy account with the bot
  @cog_ext.cog_slash(name = "register", description = "Registers an account with yvona, allowing you to earn money and have additional stats tracked.")
  async def register(self, ctx):
    user_dict = user_json.get_users()
    if str(ctx.author.id) in user_dict:
      embed = discord.Embed(title = "", description = ":no_entry: You're already registered on my database, {}.".format(ctx.author.mention))
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
              "item_level": 1,
              "damage_dealt": 0
              }
      user_dict[str(ctx.author.id)] = user
      user_json.update(user_dict)
      embed = discord.Embed(title = "", description = "You're now registered on my database, {}!".format(ctx.author.mention))
    await ctx.send(embed = embed)



  # transfers credits to another user
  @cog_ext.cog_slash(name = "transfer", description = "Transfers your money to another user.", 
    options = [create_option(
      name = "recipient",
      description = "The name of a user.",
      option_type = 6,
      required = True),
    create_option(
      name = "value",
      description = "Money value.",
      option_type = 4,
      required = True)])
  async def transfer(self, ctx, recipient: discord.Member = None, value: int = 0):
    if ctx.author == recipient:
      embed = discord.Embed(title = "", description = ":no_entry: You can't send {} to yourself, {}!".format(user_json.get_currency_name(), ctx.author.mention))

    elif value <= 0:
      embed = discord.Embed(title = "", description = ":no_entry: You can't send less than 1 {}, {}!".format(user_json.get_currency_name(), ctx.author.mention))

    elif not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = ":no_entry: It looks like you aren't registered in the system, {}. Try `/register`.".format(recipient.name, ctx.author.mention))

    elif not user_json.is_registered(recipient):
      embed = discord.Embed(title = "", description = ":no_entry: It looks like **{}** isn't registered in the system, {}".format(recipient.name, ctx.author.mention))

    else:
      user_money = user_json.get_balance(ctx.author)

      if user_money < value:
        embed = discord.Embed(title = "", description = ":no_entry: You don't have that much, {}!".format(ctx.author.mention))
        embed.set_footer(text = "You have {:,} {}.".format(user_money, user_json.get_currency_name()))
      else:
        user_json.add_balance(ctx.author, -value)
        user_json.add_balance(recipient, value)
        embed = discord.Embed(title = "", description = ":white_check_mark: {} sent {:,} {} to {}".format(ctx.author.mention, value, user_json.get_currency_name(), recipient.mention), color = ctx.author.color)
    await ctx.send(embed = embed)



  # attempts to rob a user
  @cog_ext.cog_slash(name = "rob", description = "Attempt to rob another user.", 
    options = [create_option(
      name = "user",
      description = "The name of a user.",
      option_type = 6,
      required = True),
    create_option(
      name = "money",
      description = "Money value.",
      option_type = 4,
      required = True)])
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def rob(self, ctx, user: discord.Member = None, money: int = 0):
    # checks if the user is trying to rob themselves
    if ctx.author == user:
      embed = discord.Embed(title = "", description = ":no_entry: You can't rob yourself, {}!".format(ctx.author.mention))
      await ctx.send(embed = embed)
      ctx.message = ctx
      ctx.slash.commands["rob"].reset_cooldown(ctx)

    elif money <= 0:
      embed = discord.Embed(title = "", description = ":no_entry: You need to steal more than 0 {}, {}.".format(user_json.get_currency_name(), ctx.author.mention))
      await ctx.send(embed = embed)
      ctx.message = ctx
      ctx.slash.commands["rob"].reset_cooldown(ctx)

    elif not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = ":no_entry: It looks like you aren't registered in the system, {}. Try `/register`.".format(ctx.author.mention))
      await ctx.send(embed = embed)
      ctx.message = ctx
      ctx.slash.commands["rob"].reset_cooldown(ctx)

    elif not user_json.is_registered(user):
      embed = discord.Embed(title = "", description = ":no_entry: It looks like **{}** isn't registered in the system, {}".format(user.name, ctx.author.mention))
      await ctx.send(embed = embed)
      ctx.message = ctx
      ctx.slash.commands["rob"].reset_cooldown(ctx)

    else:
      user_money = user_json.get_balance(user)

      if user_money < money:
        embed = discord.Embed(title = "", description = ":no_entry: {} doesn't have that much, {}!".format(user, ctx.author.mention))
        embed.set_footer(text = "They have {:,} {}.".format(user_money, user_json.get_currency_name()))
        ctx.slash.commands["rob"].reset_cooldown(ctx)

      else:
        success_rate = int(100-((money**1.3874)/user_money)*.98)
        if success_rate >= 90:
          success_rate = 90
        if success_rate <= 0:
          success_rate = 1

        initial_money_robber = user_json.get_balance(ctx.author)
        initial_money_target = user_json.get_balance(user)
        rand_rate = random.randint(1,100)

        if success_rate >= rand_rate:
          embed = discord.Embed(title = "Robbery successful!", description = ":white_check_mark: You stole **{:,} {}** from {}!".format(money, user_json.get_currency_name(), user.mention), color = ctx.author.color)
          user_json.add_balance(ctx.author, money)
          user_json.add_balance(user, -money)

          embed.add_field(name = ctx.author.name, value = "{:,} → {:,} {}".format(initial_money_robber, user_json.get_balance(ctx.author), user_json.get_currency_name()), inline = False)
          embed.add_field(name = user.name, value = "{:,} → {:,} {}".format(initial_money_target, user_json.get_balance(user), user_json.get_currency_name()), inline = False)

          user_dict = user_json.get_users()
          user_dict[str(ctx.author.id)]["stolen_money"] = user_dict[str(ctx.author.id)]["stolen_money"] + (money)
          user_json.update(user_dict)

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
    print(error, ctx)
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
      await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: This command is still on cooldown, {}. Try again in **{:.0f} {}**.".format(ctx.author.mention, time_left, time_unit)))
    
    if isinstance(error, commands.NotOwner):
      await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: Only the owner of the bot may run this command."))

def setup(bot):
  bot.add_cog(Economy(bot))