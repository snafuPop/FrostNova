import discord
from discord.ext import commands
from builtins import bot
import json

class General(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # ping pong!
  @commands.command(pass_context = True, description = "Checks the status of the bot")
  async def hello(self, ctx):
    embed = discord.Embed(title = "", description = ":wave:")
    await ctx.send(embed = embed)


  # hugs another user
  @commands.command(pass_context = True, description = "Hugs a user")
  async def hug(self, ctx, *, user: discord.Member = None):
    if user is None:
      embed = discord.Embed(title = "", description = "Let me know who to hug by typing in `!hug <user>`")
    else:
      embed = discord.Embed(title = "", description = "{} -> (つ≧▽≦)つ {}".format(ctx.author.mention, user.mention), color = ctx.author.color)
    await ctx.send(embed = embed)


  # gives some details about the bot
  @commands.command(alias = "[bot]", description = "Gives information about the bot")
  async def about(self, ctx):
    embed = discord.Embed(title = " ", color = 0x0080ff)
    embed.set_author(name = "Y'shtola Bot", url = "https://github.com/snafuPop/yshtola", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/482726823776485392/548612049953882143/rhuul.png")
    embed.add_field(name = "Author:", value = "snafuPop#0007", inline = True)
    embed.add_field(name = "Language:", value = "Python 3.5.x", inline = True)
    embed.add_field(name = "Discord Version", value = discord.__version__)
    embed.add_field(name = "Servers:", value = "Supporting **{}** servers".format(len(bot.guilds)))
    embed.set_footer(text = "Use !help to produce a list of commands")
    await ctx.send(embed = embed)

  # byork
  @commands.command(hidden = True, description = "byork")
  async def byork(self, ctx):
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)
    embed.set_image(url = "https://i.imgur.com/ubjESVr.png")
    await ctx.send(embed = embed)

  # prints out a list of commands
  @commands.command(description = "Prints a list of commands and what they do")
  async def help(self, ctx, *, cog_name: str = None):
    # if a cog is not provided or is not an actual cog
    if cog_name is None or cog_name.title() not in bot.cogs:
      embed = discord.Embed(title = "List of all modules", description = "Use `!help <module>` for more information")
      for cog in bot.cogs:
        embed.add_field(name = cog, value = "`!help {}`".format(cog.lower()))

    # if a cog is provided
    else:
      # applies title-case to match the names of classes
      embed = discord.Embed(title = "List of all commands in **{}**".format(cog_name.title()))
      for command in bot.get_cog(cog_name.title()).get_commands():
        if not command.hidden:
          desc = command.description
          # prevents 404 BAD REQUESTS
          if desc == "":
           desc = "oops!"
          embed.add_field(name = "`!{}`".format(str(command).replace("_", "")), value = "*{}*".format(desc), inline = False)

    # finalizing the embed
    embed.set_footer(text="Created by snafuPop#0007")
    await ctx.author.send(embed = embed)

def setup(bot):
  bot.add_cog(General(bot))