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
successful_imports = 0
total_imports = 0
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
  print("Running {}".format(discord.__version__))
  print("--------------------------------------------------------")


# prints out a list of commands
@bot.command(pass_context=True, description = "Prints a list of commands and what they do")
async def help(ctx, *, cog_name: str = None):
  # if a cog is not provided or is not an actual cog
  if cog_name is None or cog_name.title() not in bot.cogs:
    embed = discord.Embed(title = "List of all modules", description = "Use `!help <module>` for more information")
    for cog in bot.cogs:
      embed.add_field(name = cog, value = "`!help {}`".format(cog.lower()))

  # if a cog is provided
  else:
    # applies title-case to match the names of classes
    embed = discord.Embed(title = "List of all commands in **{}**".format(cog_name.title()))
    for cog in bot.cogs.keys():
      cmds = [c.name for c in discord.Bot().get_cog_commands(cog)]
      embed.add_field(name = "{cog} ({len(cmds)} Commands)", value=", ".join(cmds))
    #for command in bot.get_cog_commands(cog_name.title()):
    #  # prevents aliases
    #  if (command[0] != "_"):
    #    desc = bot.get_command(command).description
    #    # prevents 404 BAD REQUESTS
    #    if desc == "":
    #     desc = "oops!"
    #    embed.add_field(name = "`!{}".format(command), value = desc, inline = True)

  # finalizing the embed
  embed.set_footer(text="Created by snafuPop#0007")
  await channel.send_message(ctx.message.author, embed = embed)

bot.run(TOKEN)