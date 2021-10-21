import discord
from discord.ext import commands
from builtins import bot
import json
import os

class CantDo(Exception):
  pass

class InvalidArgs(Exception):
  pass


file_path = '/yvona/modules/_data/'

# get dictionary of users
def get_users():
  with open(file_path + "users.json") as json_data:
    users_dict = json.load(json_data)
  return users_dict


# get dictionary of dungeons
def get_dungeons():
  with open(file_path + "dungeons.json") as json_data:
    dungeon_dict = json.load(json_data)
  return dungeon_dict


# get dictionary of bosses
def get_bosses():
  with open(file_path + "raid.json") as json_data:
    raid_dict = json.load(json_data)
  return raid_dict

# updates the dictionary of bosses
def update_bosses(boss_dict):
  with open(file_path + "raid.json", "w") as json_out:
    json.dump(boss_dict, json_out, indent = 2)

# updates the .json with new values and creates a back-up
def update(user_dict):
  with open(file_path + "users.json", "w") as json_out:
    json.dump(user_dict, json_out, indent = 2)


# returns the name of the currency
def get_currency_name():
  return "pennies"


# returns the payday value
def get_payday():
  return 500


# returns all keys stored by the user key
def get_keys():
  user_dict = get_users()
  return user_dict["94236862280892416"].keys()


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


# adds an item to the user
def add_item(user, item):
  user_dict = get_users()
  user_dict[str(user.id)]["inventory"].append(str(item))
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

def add_loot_earnings(user, money):
  user_dict = get_users()
  user_dict[str(user.id)]["loot_earnings"] = user_dict[str(user.id)]["loot_earnings"] + money
  update(user_dict)

def add_raid(user):
  user_dict = get_users()
  user_dict[str(user.id)]["raids"] = user_dict[str(user.id)]["raids"] + 1
  update(user_dict)

def add_damage_dealt(user, damage):
  user_dict = get_users()
  user_dict[str(user.id)]["damage_dealt"] = user_dict[str(user.id)]["damage_dealt"] + damage
  update(user_dict)

async def add_exp(ctx, user, exp):
  user_dict = get_users()
  user_dict[str(user.id)]["exp"] = user_dict[str(user.id)]["exp"] + exp
  update(user_dict)
  if level_up(user):
    embed = discord.Embed(title = "***Level Up!***", description = "{} has leveled up from {} to ***{}***!".format(user.mention, user_dict[str(user.id)]["level"], user_dict[str(user.id)]["level"]+1), color = user.color)
    embed.set_footer(text = "Overflow EXP has been converted to {}.".format(get_currency_name()))
    await ctx.send(embed = embed)


def level_up(user):
  user_dict = get_users()
  req_exp = get_req_exp(user, user_dict)
  if user_dict[str(user.id)]["exp"] >= req_exp:
    # incrementing the level
    user_dict[str(user.id)]["level"] = user_dict[str(user.id)]["level"] + 1

    # dealing with overflow EXP
    user_dict[str(user.id)]["exp"] = 0
    update(user_dict)
    return True
  return False


def get_req_exp(user, user_dict):
  return int((user_dict[str(user.id)]["level"]**3.9)+100)
