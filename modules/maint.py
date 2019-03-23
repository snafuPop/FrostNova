import discord
from discord.ext import commands
from builtins import bot
from .utils import perms

class Maint:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(description = "Shuts down the bot.")
  async def shutdown(self):
    # shuts down the bot

    embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")
    await self.bot.say(embed = embed)
    await self.bot.logout()

  @perms.is_owner()
  @commands.command(description = "Reloads a module.")
  async def reload(self, *, module: str = None):
    # reloads a module

    if module is None:
      embed = discord.Embed(title = "", description = "Try loading a module with `!reload <module>`")
    else:
      load_module = "modules." + module
      try:
        self.bot.unload_extension(load_module)
        self.bot.load_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be reloaded. Check the terminal and the message bellow for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = "**{}** was reloaded successfully!".format(module))

    await self.bot.say(embed = embed)

def setup(bot):
  bot.add_cog(Maint(bot))