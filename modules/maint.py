import discord
from discord.ext import commands
from builtins import bot
from .utils import perms

@bot.command(description = "Shuts down the bot.")
async def shutdown():
  # shuts down the bot
  embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")

  await bot.logout()

@perms.is_owner()
@bot.command(description = "Reloads a module.")
async def reload(*, module: str = None):

  if module is None:
    embed = discord.Embed(title = "", description = "Try loading a module with `!reload <module>`")
  else:
    try:
      bot.unload_extension(module)
      bot.load_extension(module)
    except Exception as e:
      embed = discord.Embed(title = "", description = "**{}** could not be reloaded. Check the terminal and the message bellow for more information.".format(module))
      embed.add_field(name = type(e).__name__, value = e)
    else:
      embed = discord.Embed(title = "", description = "**{}** was reloaded successfully!".format(module))

  await bot.say(embed = embed)