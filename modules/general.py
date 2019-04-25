import discord
from discord.ext import commands
from builtins import bot
import time
import datetime
import sys
import psutil
from modules.utils import user_json


class General(commands.Cog):
  def __init__(self, bot):
    self.time_alive = time.time()
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

  # gets leadership info
  @commands.command(aliases = ["top", "best", "rank"], description = "Gets leaderboard information")
  async def leaderboard(self, ctx):
    embed = discord.Embed(title = ":trophy: Leaderboard", description = "Requested by {}".format(ctx.author.mention), color = ctx.author.color)
    self.top_five(embed, 'balance', 'Richest Users')
    self.top_five(embed, 'text_posts', 'Chattiest Users')
    self.top_five(embed, 'level', 'Highest Levels')
    embed.set_footer(text = "Only registered users are tracked. Type !register to start tracking your records (and more)!")
    await ctx.send(embed = embed)

  # helper method to append a field that contains leaderboard information
  def top_five(self, embed, parameter, title):
    medals = [":first_place:", ":second_place:", ":third_place:", ":medal:", ":military_medal:"]
    users = user_json.get_users()
    user_list = sorted(users, key = lambda x: (users[x][parameter]), reverse = True)
    user_list.remove("547516876851380293") # hiding y'shtola from the list
    top_users = ""
    for i in range(len(medals)):
      top_users += "\u3164{} **{}**: {:,}\n".format(medals[i], users[user_list[i]]['username'], users[user_list[i]][parameter])
    embed.add_field(name = "**__{}__**".format(title), value = top_users, inline = True)

  # gives some details about the bot
  @commands.command(aliases = ["bot", "info"], description = "Gives information about the bot")
  async def about(self, ctx):
    embed = discord.Embed(title = " ", color = 0x0080ff)
    embed.set_author(name = "Y'shtola Bot", url = "https://github.com/snafuPop/yshtola", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/482726823776485392/548612049953882143/rhuul.png")

    # storing info onto a string to make things a little more readable
    info  = "**Author:** snafuPop#0007\n"
    info += "**Language:** Python {}.{}.{}\n".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
    info += "**Discord.py Version:** {}\n".format(discord.__version__)
    info += "**CPU Usage:** {}%\n".format(psutil.cpu_percent())
    info += "**Disk Usage:** {}%\n".format(psutil.disk_usage('/')[3])
    info += "**Current Uptime:** {}\n".format(self.get_uptime())
    info += "**Servers:** {:,} ({:,} users)\n".format(len(bot.guilds), len(bot.users))
    info += "\nWant y'shtola on _your_ server? [Click here](https://discordapp.com/api/oauth2/authorize?client_id=547516876851380293&permissions=1861483585&scope=bot)\n"

    embed.add_field(name = "\u3164", value = info)
    embed.set_footer(text = "Use !help to produce a list of commands")
    await ctx.send(embed = embed)


  def get_uptime(self):
    current_time = time.time()
    difference = int(current_time - self.time_alive)
    return str(datetime.timedelta(seconds=difference))


  # byork
  @commands.command(hidden = True, description = "byork")
  async def byork(self, ctx):
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)
    embed.set_image(url = "https://i.imgur.com/ubjESVr.png")
    await ctx.send(embed = embed)


  # glue
  @commands.command(hidden = True, description = "glue")
  async def glue(self, ctx):
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)
    embed.set_image(url = "https://i.imgur.com/CyTsoeL.png")
    await ctx.send(embed = embed)

  # undertale
  @commands.command(hidden = True, description = "undertale")
  async def undertale(self, ctx):
    embed = discord.Embed(title = "", description = ctx.author.mention, color = ctx.author.color)
    embed.set_image(url = "https://66.media.tumblr.com/09d760e5a4d8ba210642394dbeff578c/tumblr_otihzoKUwR1qhzw8jo2_500.png")
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