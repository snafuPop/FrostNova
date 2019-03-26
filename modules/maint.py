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

  # unloads a module
  @perms.is_owner()
  @commands.command(description = "Unloads a module.")
  async def unload(self, *, module: str = None):
    if module is None:
      embed = discord.Embed(title = "", description = "Try unloading a module with `!unload <module>`")
    else:
      load_module = "modules." + module
      try:
        self.bot.unload_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be unloaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = "**{}** was unloaded successfully.".format(module))
        print("\n\n{} was unloaded.".format(module))
        print("--------------------------------------------------------")
    await self.bot.say(embed = embed)

  # loads a module
  @perms.is_owner()
  @commands.command(description = "Loads a module.")
  async def load(self, *, module: str = None):
    if module is None:
      embed = discord.Embed(title = "", description = "Try loading a module with `!load <module>`")
    else:
      load_module = "modules." + module
      try:
        self.bot.load_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be loaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = "**{}** was loaded successfully.".format(module))
        print("\n\n{} was loaded.".format(module))
        print("--------------------------------------------------------")
    await self.bot.say(embed = embed)

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
        embed = discord.Embed(title = "", description = "**{}** could not be reloaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = "**{}** was reloaded successfully.".format(module))
        print("\n\n{} was reloaded.".format(module))
        print("--------------------------------------------------------")
    await self.bot.say(embed = embed)

def setup(bot):
  bot.add_cog(Maint(bot))