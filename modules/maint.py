import discord
from discord.ext import commands
from builtins import bot
from modules.utils import perms

class Maint:
  def __init__(self, bot):
    self.bot = bot

  # shuts down the bot
  @perms.is_owner()
  @commands.command(description = "Shuts down the bot.")
  async def shutdown(self):
    embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")
    await self.bot.say(embed = embed)
    await self.bot.logout()

  # reloads a module
  @perms.is_owner()
  @commands.command(description = "Reloads a module.")
  async def reload(self, *, module: str = None):
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
        print("\n\n{} was reloaded.".format(module))
        print("--------------------------------------------------------")

    await self.bot.say(embed = embed)

def setup(bot):
  bot.add_cog(Maint(bot))