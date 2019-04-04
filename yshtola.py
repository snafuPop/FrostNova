from os.path import dirname, basename, isfile
import sys
import glob
import os
import builtins
import importlib
import inspect
from enum import Enum
import json

# attempt to import discord.py
try:
  import discord
  from discord.ext import commands
except ImportError:
  print("discord.py was not found.")
  sys.exit(1)

# load the token and prefix
with open("/home/snafuPop/yshtola/_config/settings.json") as json_data:
  TOKEN = json.load(json_data)["TOKEN"]
bot = commands.Bot(command_prefix='!')
builtins.bot = bot
bot.remove_command('help')


# imports
successful_imports = 0
total_imports = 0
print("\n")
for file in os.listdir("/home/snafuPop/yshtola/modules/"):
  filename = os.fsdecode(file)
  if filename != "__init__.py" and filename.endswith(".py"):
    total_imports += 1
    try:
      bot.load_extension("modules." + filename[:-3])
      print("{} was loaded successfully!".format(filename))
      successful_imports += 1
    except Exception as e:
      print("{} had some problems ({}: {})".format(filename, type(e).__name__, e))


@bot.event
async def on_ready():
  # runs when the bot is fully functional
  print("\n{}/{} modules loaded".format(successful_imports, total_imports))
  print("Logged in as {} <{}>".format(bot.user.name, bot.user.id))
  print("Running {}".format(discord.__version__))
  print("--------------------------------------------------------")


bot.run(TOKEN)