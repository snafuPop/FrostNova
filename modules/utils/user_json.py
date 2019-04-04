import discord
from discord.ext import commands
from builtins import bot
import json

class CantDo(Exception):
  pass

class InvalidArgs(Exception):
  pass


# get dictionary of users
def get_users():
  with open("/home/snafuPop/yshtola/modules/_data/users.json") as json_data:
    users_dict = json.load(json_data)
  return users_dict


# updates the .json with new values and creates a back-up
def update(user_dict):
  with open("/home/snafuPop/yshtola/modules/_data/users.json", "w") as json_out:
    json.dump(user_dict, json_out, indent = 2)


# returns the name of the currency
def get_currency_name():
  return "pennies"


# returns the payday value
def get_payday():
  return 500


# checks if the user is registered within the system
def is_registered(user):
  user_dict = get_users()
  return str(user.id) in user_dict


# returns the balance of a specified user
def get_balance(user):
  user_dict = get_users()
  return user_dict[str(user.id)]["balance"]


# adds (or subtracts) credits to/from a user
def add_balance(user, credits):
  user_dict = get_users()
  user_dict[str(user.id)]["balance"] = user_dict[str(user.id)]["balance"] + credits
  update(user_dict)


# checks if the user can pay for a certain action
def can_spend(user, cost):
  return get_balance(user) >= cost


# checks through basic requirements for using economy actions
# if everything is okay, we return the money value back
async def can_do(ctx, user, money):
  if not is_registered(user):
    embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(user.mention))
    await ctx.send(embed = embed)
    raise CantDo

  # checks for strings as input
  money = interpret_frac(user, money)

  # nothing particular happens -- should be handled by individual methods through a try-catch
  if money is None:
    raise InvalidArgs

  # if money is a value less than or equal to 0
  elif money <= 0:
    embed = discord.Embed(title = "", description = "You need to spend more than 0 {}, {}.".format(get_currency_name(), user.mention))
    await ctx.send(embed = embed)
    raise CantDo

  # if the money is more than the user can spend
  elif not can_spend(user, money):
    embed = discord.Embed(title = "", description = "You don't have enough {} for that, {}!".format(get_currency_name(), user.mention))
    await ctx.send(embed = embed)
    raise CantDo

  return money


# allows users to give fractional strings as arguments and interprets them into integer values
def interpret_frac(user, money):
  if money == None:
    return
  if money.isdigit():
    return int(money)
  if money == "all":
    return get_balance(user)
  if money == "half":
    return get_balance(user)//2
  if money == "fourth":
    return get_balance(user)//4
  if money == "tenth":
    return get_balance(user)//10
  return