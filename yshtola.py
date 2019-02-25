import discord
import builtins
from discord.ext import commands
import importlib
import inspect
from enum import Enum
import json

with open("_config/settings.json") as json_data:
  TOKEN = json.load(json_data)["TOKEN"]

bot = commands.Bot(command_prefix='!')
builtins.bot = bot
bot.remove_command('help')

from modules.general import *
from modules.roll import *
from modules.wiki import *
from modules.maint import *
from modules.witchy import *
from modules.reddit import *

@bot.event
async def on_ready():
  # runs when the bot is fully functional

  print('Logged in as', bot.user.name, bot.user.id)
  print('------')

@bot.command(pass_context=True)
async def help(ctx):
  # prints commands
  pass

bot.run(TOKEN)