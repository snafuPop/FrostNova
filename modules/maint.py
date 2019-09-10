import discord
from discord.ext import commands
from builtins import bot
from modules.utils import perms
import json

class Maint(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # shuts down the bot
  @commands.is_owner()
  @commands.command(hidden = True, description = "Shuts down the bot.")
  async def shutdown(self, ctx):
    embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")
    await ctx.send(embed = embed)
    await self.bot.logout()

  # unloads a module
  @commands.is_owner()
  @commands.command(hidden = True, description = "Unloads a module.")
  async def unload(self, ctx, *, module: str = None):
    if module is None:
      embed = discord.Embed(title = "", description = "Try unloading a module with `{}unload <module>`".format(ctx.prefix))
    else:
      load_module = "modules." + module
      try:
        self.bot.unload_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be unloaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = ":eject: **{}** was unloaded successfully.".format(module))
        print("\n\n{} was unloaded.".format(module))
        print("--------------------------------------------------------")
    await ctx.send(embed = embed)

  # loads a module
  @commands.is_owner()
  @commands.command(hidden = True, description = "Loads a module.")
  async def load(self, ctx, *, module: str = None):
    if module is None:
      embed = discord.Embed(title = "", description = "Try loading a module with `{}load <module>`".format(ctx.prefix))
    else:
      load_module = "modules." + module
      try:
        self.bot.load_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be loaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = ":record_button: **{}** was loaded successfully.".format(module))
        print("\n\n{} was loaded.".format(module))
        print("--------------------------------------------------------")
    await ctx.send(embed = embed)

  # reloads a module
  @commands.is_owner()
  @commands.command(hidden = True, description = "Reloads a module.")
  async def reload(self, ctx, *, module: str = None):
    if module is None:
      embed = discord.Embed(title = "", description = "Try loading a module with `{}reload <module>`".format(ctx.prefix))
    else:
      load_module = "modules." + module
      try:
        self.bot.reload_extension(load_module)
      except Exception as e:
        embed = discord.Embed(title = "", description = "**{}** could not be reloaded. Check the terminal and the message below for more information.".format(module))
        embed.add_field(name = type(e).__name__, value = e)
      else:
        embed = discord.Embed(title = "", description = ":repeat: **{}** was reloaded successfully.".format(module))
        print("\n\n{} was reloaded.".format(module))
        print("--------------------------------------------------------")
    await ctx.send(embed = embed)

  # flushes logs
  @commands.is_owner()
  @commands.command(hidden = True, description = "Flushes output to the console.")
  async def flush(self, ctx):
    print("Flushing!\n----------------------------\n", flush = True)
    await ctx.send(embed = discord.Embed(title = "", description = "Flushed logs."))

  @commands.is_owner()
  @commands.command(hidden = True, description = "Changes the bot's name.")
  async def rename(self, ctx, *, new_name: str = None):
    if new_name is None:
      await ctx.send(embed = discord.Embed(title = "", description = "Invalid name."))
    else:
      original_name = self.bot.user.name
      await self.bot.user.edit(username = new_name)
      await ctx.send(embed = discord.Embed(title = "", description = "Changed my name from **{}** to **{}**".format(original_name, bot.user.name)))

  @commands.is_owner()
  @commands.command(hidden = True, description = "Causes the bot to leave the server.")
  async def leave(self, ctx):
    try:
      await ctx.guild.leave
    except:
      embed = discord.Embed(title = "", descritpion = "だが断る。")
      embed.set_image(url = "https://i.kym-cdn.com/photos/images/original/001/178/131/588.gif")
      await ctx.send(embed = embed)

  @commands.command(description = "Changes the server's custom prefix for this bot. Must have guild modification privileges.")
  async def prefix(self, ctx, prefix: str = None):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to change my prefix."))
      return
    with open("/home/snafuPop/yshtola/_config/settings.json") as json_data:
      settings = json.load(json_data)
    guild_id = str(ctx.guild.id)
    if prefix is None:
      current_prefix = settings["PREFIXES"][guild_id] if guild_id in settings["PREFIXES"] else "!"
      embed = discord.Embed(title = "**Current server prefix:** `{}`".format(current_prefix), description = "You can set a custom prefix for this server with `{}prefix <prefix>`, {}.".format(ctx.prefix, ctx.author.mention))
      embed.set_footer(text = "You can place an underscore at the end of a prefix to signify a space.")
      await ctx.send(embed = embed)
    else:
      if prefix != "_" and prefix.endswith("_"):
        prefix = prefix[:-1] + " "
      settings["PREFIXES"][guild_id] = prefix
      with open("/home/snafuPop/yshtola/_config/settings.json", "w") as json_out:
        json.dump(settings, json_out, indent = 2)
      await ctx.send(embed = discord.Embed(title = "Prefix successfully changed!", description = "I've set the prefix for this server to `{}`, {}.".format(prefix, ctx.author.mention)))

def setup(bot):
  bot.add_cog(Maint(bot))