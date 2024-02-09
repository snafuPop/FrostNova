import discord
from discord import app_commands
from discord.ext import commands

import json
import os

class CantDo(Exception):
  pass

class InvalidArgs(Exception):
  pass


file_path = '/home/ec2-user/frostnova/cogs/_data/'

# get dictionary of users
def get_users():
  with open(file_path + "users.json") as json_data:
    users_dict = json.load(json_data)
  return users_dict


# get an individual user
def get_user(user_id):
  with open(file_path + "users.json") as json_data:
    users_dict = json.load(json_data)
  return users_dict[str(user_id)]


# updates the .json with new values and creates a back-up
def update(user_dict):
  with open(file_path + "users.json", "w") as json_out:
    json.dump(user_dict, json_out, indent = 2)


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


def add_slot_winnings(user, value):
  user_dict = get_users()
  user_dict[str(user.id)]["slot_winnings"] = user_dict[str(user.id)]["slot_winnings"] + (value)
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
