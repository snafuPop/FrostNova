import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids
from modules.utils import perms
import os
import json

class Maint(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # shuts down the bot
  @commands.is_owner()
  @cog_ext.cog_slash(name = "shutdown", description = "⛔ Shuts down the bot.")
  async def shutdown(self, ctx):
    await ctx.defer()
    embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")
    await ctx.send(embed = embed)
    await self.bot.logout()


  @commands.is_owner()
  @cog_ext.cog_slash(name = "unload", description = "⛔ Unloads a module.", 
    options = [create_option(
      name = "module",
      description = "The name of the module to be unloaded.",
      option_type = 3,
      required = True,
      choices = [
        create_choice(
          name = module, 
          value = module)
        for module in os.listdir("modules") if module.endswith(".py")
      ])
    ])
  async def unload(self, ctx, module: str = None):
    await ctx.defer()
    load_module = "modules." + module[:len(module)-3]
    try:
      self.bot.unload_extension(load_module)
    except Exception as e:
      embed = discord.Embed(title = "", description = f":no_entry: **{module}** could not be unloaded. Check the terminal and the message below for more information.")
      embed.add_field(name = type(e).__name__, value = e)
    else:
      embed = discord.Embed(title = "", description = f":eject: **{module}** was unloaded successfully.")
      print("{} was unloaded.".format(module))
    await ctx.send(embed = embed)


  @commands.is_owner()
  @cog_ext.cog_slash(name = "load", description = "⛔ Loads a module.", 
    options = [create_option(
      name = "module",
      description = "The name of the module to be unloaded.",
      option_type = 3,
      required = True,
      choices = [
        create_choice(
          name = module, 
          value = module)
        for module in os.listdir("modules") if module.endswith(".py")
      ])
    ])
  async def load(self, ctx, module: str = None):
    await ctx.defer()
    load_module = "modules." + module[:len(module)-3]
    try:
      self.bot.load_extension(load_module)
    except Exception as e:
      embed = discord.Embed(title = "", description = f":no_entry: **{module}** could not be loaded. Check the terminal and the message below for more information.")
      embed.add_field(name = type(e).__name__, value = e)
    else:
      embed = discord.Embed(title = "", description = f":record_button: **{module}** was loaded successfully.")
      print("{} was loaded.".format(module))
    await ctx.send(embed = embed)


  @commands.is_owner()
  @cog_ext.cog_slash(name = "reload", description = "⛔ Reloads a module. Leave moudle field empty to reload all modules.",
    options = [create_option(
      name = "module",
      description = "The name of the module to be reloaded.",
      option_type = 3,
      required = False,
      choices = [
        create_choice(
          name = module, 
          value = module)
        for module in os.listdir("modules") if module.endswith(".py")
      ])
    ])
  async def reload(self, ctx, module: str = None):
    await ctx.defer()
    if (module is None):
      for module in os.listdir("modules"):
        if (module.endswith(".py")):
          try:
            self.bot.reload_extension("modules." + module[:len(module)-3])
            print("{} was reloaded.".format(module))
          except Exception as e:
            embed = discord.Embed(title = "", description = f":no_entry: **{module}** could not be reloaded. Check the terminal and the message below for more information.")
            embed.add_field(name = type(e).__name__, value = e)
          else:
            embed = discord.Embed(title = "", description = ":repeat: All modules were reloaded successfully.")
    else:
      try:
        self.bot.reload_extension("modules." + module[:len(module)-3])
      except Exception as e:
        embed = discord.Embed(title = "", description = f":no_entry: **{module}** could not be reloaded. Check the terminal and the message below for more information.")
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = f":repeat: **{module}** was reloaded.")
        print("{} was reloaded.".format(module))
    await ctx.send(embed = embed)


@bot.event
async def on_slash_command_error(ctx, error):
  print(error, ctx)
  if isinstance(error, commands.NotOwner):
    embed = discord.Embed(title = "", description = ":no_entry: Only the owner of the bot may run this command.")
    await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Maint(bot))