import discord
from discord.ext import commands
from .utils import perms

@bot.command()
async def shutdown():
  # shuts down the bot
  await bot.logout()

@perms.is_owner()
@bot.command()
async def reload(*, module: str):
    """Reloads a module."""
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await bot.say('\N{PISTOL}')
        await bot.say('{}: {}'.format(type(e).__name__, e))
    else:
        await bot.say('\N{OK HAND SIGN}')