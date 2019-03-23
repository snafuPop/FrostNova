from os.path import dirname, basename, isfile
import glob
import os
import builtins
import importlib
import inspect
from enum import Enum
import json

# attempt to import discord.py
try:
  from discord.ext import commands
  import discord
except ImportError:
  print("discord.py was not found.")
  sys.exit(1)

# load the token and prefix
with open("_config/settings.json") as json_data:
  TOKEN = json.load(json_data)["TOKEN"]
bot = commands.Bot(command_prefix='!')
builtins.bot = bot
bot.remove_command('help')

# imports
successful_imports = 0;
total_imports = 0;
print("\n")
for file in os.listdir("modules/"):
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
  print("--------------------------------------------------------")

@bot.command(pass_context=True, description = "Prints a list of commands and what they do")
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