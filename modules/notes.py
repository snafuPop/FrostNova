import discord
from discord.ext import commands
from builtins import bot
import random
import json

class Notes(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def get_notebook(self):
    with open("/home/snafuPop/yshtola/modules/_data/notes.json") as json_data:
      notebook = json.load(json_data)
    return notebook

  def update(self, notebook):
    with open("/home/snafuPop/yshtola/modules/_data/notes.json", "w") as json_out:
      json.dump(notebook, json_out, indent = 2)

  @commands.command(aliases = ["notebook"], description = "Browse through all saved notes (saved by guild).")
  async def notes(self, ctx):
    if ctx.guild is None:
      await ctx.send(embed = discord.Embed(title = "Not in a server", description = "You need to be in a server to read notes, {}.".format(ctx.author.mention)))
      return
    guild_id = str(ctx.guild.id)
    notebook = self.get_notebook()
    if guild_id not in notebook["server"] or not notebook["server"][guild_id]:
      await ctx.send(embed = discord.Embed(title = "", description = "It doesn't look like this server has any notes. Try writing one using `!write`, {}!".format(ctx.author.mention)))
    else:
      page = ""
      for key in notebook["server"][guild_id]:
        page += "**{}**, ".format(str(key))
      embed = discord.Embed(title = "**Notebook for {}**".format(ctx.guild), description = "Requested by {}.".format(ctx.author.mention), color = ctx.author.color)
      embed.add_field(name = "\u3164", value = page[:-2])
      embed.set_footer(text = "Use {}read to read a note".format(ctx.prefix))
      await ctx.send(embed = embed)

  @commands.command(aliases = ["bulletin"], description = "Browse through all saved announcements (viewable by everyone).")
  async def announcements(self, ctx):
    notebook = self.get_notebook()
    if not notebook["public"]:
      await ctx.send(embed = discord.Embed(title = "", description = "It doesn't look like there are any announcements. Try writing one using `!announce`, {}!".format(ctx.author.mention)))
    else:
      page = ""
      for key in notebook["public"]:
        page += "**{}**, ".format(str(key))
      embed = discord.Embed(title = "**Public Announcements**".format(ctx.guild), description = "Requested by {}.".format(ctx.author.mention), color = ctx.author.color)
      embed.add_field(name = "\u3164", value = page[:-2])
      embed.set_footer(text = "Use {}view to read an announcement".format(ctx.prefix))
      await ctx.send(embed = embed)

  @commands.command(description = "Read a note.")
  async def read(self, ctx, *, title: str = None):
    if ctx.guild is None:
      await ctx.send(embed = discord.Embed(title = "Not in a server", description = "You need to be in a server to read notes, {}.".format(ctx.author.mention)))
      return
    if title is None:
      await ctx.send(embed = discord.Embed(title = "", description = "You can read a note by using `{}read <title of note>`, {}.".format(ctx.prefix, ctx.author.mention)))
    else:
      guild_id = str(ctx.guild.id)
      notebook = self.get_notebook()
      if title not in notebook["server"][guild_id]:
        await ctx.send(embed = discord.Embed(title = "", description = "Could not find a note with the title **\"{}\"**, {}.".format(title, ctx.author.mention)))
      else:
        note = notebook["server"][guild_id][title]
        user = await self.bot.fetch_user(note[1])
        embed = discord.Embed(title = "**{}**".format(title), description = note[0], color = user.color)
        embed.set_footer(text = "Original author: {}".format(user), icon_url = user.avatar_url)
        await ctx.send(embed = embed)

  @commands.command(description = "Read an announcement.")
  async def view(self, ctx, *, title: str = None):
    if title is None:
      await ctx.send(embed = discord.Embed(title = "", description = "You can view an announcement by using `{}announce <title of announcement>`, {}.".format(ctx.prefix, ctx.author.mention)))
    else:
      notebook = self.get_notebook()
      if title not in notebook["public"]:
        await ctx.send(embed = discord.Embed(title = "", description = "Could not find an announcement with the title **\"{}\"**, {}.".format(title, ctx.author.mention)))
      else:
        note = notebook["public"][title]
        user = await self.bot.fetch_user(note[1])
        embed = discord.Embed(title = "**{}**".format(title), description = note[0], color = user.color)
        embed.set_footer(text = "Original author: {}".format(user), icon_url = user.avatar_url)
        await ctx.send(embed = embed)

  @commands.command(description = "Write a note.")
  async def write(self, ctx, *args):
    if ctx.guild is None:
      await ctx.send(embed = discord.Embed(title = "Not in a server", description = "You need to be in a server to write notes, {}.".format(ctx.author.mention)))
      return
    if len(args) != 2:
      embed = discord.Embed(title = "", description = "You can write a note with `{}write \"<title>\" \"<body>\"`, {}".format(ctx.prefix, ctx.author.mention))
      embed.set_footer(text = "These notes can only be read by members of this server.")
      await ctx.send(embed = embed)
    else:
      guild_id = str(ctx.guild.id)
      notebook = self.get_notebook()
      if guild_id not in notebook["server"]:
        notebook["server"][guild_id] = {}
      if args[0] in notebook["server"][guild_id]:
        await ctx.send(embed = discord.Embed(title = "**Error!**", description = "There is already a note with the title {}, {}. Try a different title.".format(args[0], ctx.author.mention)))
      else:
        notebook["server"][guild_id][args[0]] = [args[1], ctx.author.id]
        self.update(notebook)
        embed = discord.Embed(title = "**Note saved!**", description = "Written by {}".format(ctx.author.mention), color = ctx.author.color)
        embed.add_field(name = "**{}**".format(args[0]), value = args[1])
        await ctx.send(embed = embed)

  @commands.command(description = "Write an announcement.")
  async def announce(self, ctx, *args):
    if len(args) != 2:
      embed = discord.Embed(title = "", description = "You can announce something with `{}announce \"<title>\" \"<body>\"`, {}".format(ctx.prefix, ctx.author.mention))
      embed.set_footer(text = "Announcements are saved across all servers, and can be read by anybody.")
      await ctx.send(embed = embed)
    else:
      notebook = self.get_notebook()
      if args[0] in notebook["public"]:
        await ctx.send(embed = discord.Embed(title = "**Error!**", description = "There is already an announcemnt with the title {}, {}. Try a different title.".format(args[0], ctx.author.mention)))
      else:
        notebook["public"][args[0]] = [args[1], ctx.author.id]
        self.update(notebook)
        embed = discord.Embed(title = "**Announcement saved!**", description = "Written by {}".format(ctx.author.mention), color = ctx.author.color)
        embed.add_field(name = "**{}**".format(args[0]), value = args[1])
        await ctx.send(embed = embed)

  @commands.command(description = "Erase a note.")
  async def erase(self, ctx, title: str = None):
    if ctx.guild is None:
      await ctx.send(embed = discord.Embed(title = "Not in a server", description = "You need to be in a server to erase notes, {}.".format(ctx.author.mention)))
      return
    if title is None:
      await ctx.send(embed = discord.Embed(title = "", description = "You can delete an existing note by using `{}erase <title of note>`, {}.".format(ctx.prefix, ctx.author.mention)))
    else:
      guild_id = str(ctx.guild.id)
      notebook = self.get_notebook()
      if title not in notebook["server"][guild_id]:
        await ctx.send(embed = discord.Embed(title = "", description = "Could not find a note with the title **\"{}\"**, {}.".format(title, ctx.author.mention)))
      else:
        notebook["server"][guild_id].pop(title)
        self.update(notebook)
        await ctx.send(embed = discord.Embed(title = "", description = "Deleted note entitled **\"{}\"**, {}.".format(title, ctx.author.mention), color = ctx.author.color))

  @commands.command(description = "Erase an announcement.")
  async def unannounce(self, ctx, title: str = None):
    if title is None:
      await ctx.send(embed = discord.Embed(title = "", description = "You can delete an existing announcement by using `{}unannounce <title of announcement>`, {}.".format(ctx.prefix, ctx.author.mention)))
    else:
      notebook = self.get_notebook()
      if title not in notebook["public"]:
        await ctx.send(embed = discord.Embed(title = "", description = "Could not find a note with the title **\"{}\"**, {}.".format(title, ctx.author.mention)))
      else:
        notebook["public"].pop(title)
        self.update(notebook)
        await ctx.send(embed = discord.Embed(title = "", description = "Deleted note entitled **\"{}\"**, {}.".format(title, ctx.author.mention), color = ctx.author.color))

def setup(bot):
  bot.add_cog(Notes(bot))