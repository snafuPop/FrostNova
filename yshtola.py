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
  print('--------------------------------------------------------')

@bot.command(pass_context=True, description = "Prints a list of commands and what they do.")
async def help(ctx):
  # prints commands

  embed = discord.Embed(title = "List of all commands", description = "")
  embed.set_footer(text="Created by snafuPop#0007")

  # iterating through list of commands attached to bot
  for command in bot.commands:

    # filters out commands aliases
    if (command[0] != "_"):

      # gives commands without a description a placeholder description so as to not trigger a 400 BAD REQUEST
      desc = bot.get_command(command).description
      if desc == "":
        desc = "does it."

      # appends a field for each command
      embed.add_field(name = "`!{}`".format(command), value = desc, inline = False)

  # sends a DM to the user who requested !help
  await bot.send_message(ctx.message.author, embed = embed)

bot.run(TOKEN)