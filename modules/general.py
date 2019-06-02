import discord
from discord.ext import commands
from builtins import bot
import time
import datetime
import sys
import psutil
from modules.utils import user_json
from random import randint


class General(commands.Cog):
  def __init__(self, bot):
    self.time_alive = time.time()
    self.bot = bot

  # this is a listener that sends a welcome message when the bot joins a guild
  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    for channel in guild.text_channels:
      if channel.permissions_for(guild.me).send_messages:
        embed = discord.Embed(title = "**Hello!** :wave:", description = "Thank you for inviting me to your server. For a list of commands, type `!help`.")
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        embed.set_footer(text = "As an admin, you can also change the prefix used by using !prefix <prefix>.")
        await channel.send(embed = embed)
        break


  # ping pong!
  @commands.command(aliases = ["wave", "ping"], description = "Checks the status of the bot")
  async def hello(self, ctx):
    embed = discord.Embed(title = "", description = "Hi, {}! :wave:".format(ctx.author.mention))
    await ctx.send(embed = embed)

  # rates a user's nickname
  @commands.command(description = "Rate a username!")
  async def nickometer(self, ctx, *, user: discord.Member = None):
    if user is None:
      user = ctx.author
    rating = 100
    marks = ""

    # loss for generic user ID
    if user.discriminator in ["0000", "0001", "6969", "4200", "9999"]:
      marks += "\u3164**-50** Edgy discriminator ({})\n".format(user.discriminator)
      rating -= 50

    # loss for weeb
    if any(i in user.display_name.lower() for i in ["chan", "sama", "hime", "kitsune", "tsuki", "neko", "senpai"]):
      marks += "\u3164**-40** Weeaboo\n"
      rating -= 40

    # loss for number in name
    if any(char.isdigit() for char in user.display_name):
      marks += "\u3164**-20** Numbers in username\n"
      rating -= 20

    # loss for non single-word name
    if " " in user.display_name:
      marks += "\u3164**-10** Space in name\n"
      rating -= 10

    # loss for name ending with an "a"
    if user.display_name.lower().endswith("a"):
      marks += "\u3164**-10** Name ends with an \"a\"\n"
      rating -= 10

    if marks == "":
      marks = "\u3164No negative marks! Good job!"

    embed = discord.Embed(title = "**Nickometer Rating**", description = "Rating {}'s name".format(user.mention), color = user.color)
    embed.add_field(name = "**Overall Rating:** {}".format(rating), value = marks)
    await ctx.send(embed = embed)

  # hugs another user
  @commands.command(pass_context = True, description = "Hugs a user")
  async def hug(self, ctx, *, user: discord.Member = None):
    if user is None:
      embed = discord.Embed(title = "", description = "Let me know who to hug by typing in `{}hug <user>`, {}.".format(ctx.prefix, ctx.author.mention))
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
    embed.set_footer(text = "Only registered users are tracked. Type {}register to start tracking your records (and more)!".format(ctx.prefix))
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
    embed = discord.Embed(title = " ", color = bot.user.color)
    embed.set_author(name = "Y'shtola Bot", url = "https://github.com/snafuPop/yshtola", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = self.bot.user.avatar_url)

    # storing info onto a string to make things a little more readable
    info  = "**\u3164\u25A0 Author:** {}\n".format(await self.bot.fetch_user(self.bot.owner_id))
    info += "**\u3164\u25A0 Language:** Python {}.{}.{}\n".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
    info += "**\u3164\u25A0 Discord.py Version:** {}\n".format(discord.__version__)
    info += "**\u3164\u25A0 Host:** [PythonAnywhere](https://www.pythonanywhere.com/)\n"
    info += "**\u3164\u25A0 Latency:** {:.4f} ms\n".format(self.bot.latency)
    info += "**\u3164\u25A0 CPU Usage:** {}%\n".format(psutil.cpu_percent())
    info += "**\u3164\u25A0 Disk Usage:** {}%\n".format(psutil.disk_usage('/')[3])
    info += "**\u3164\u25A0 Current Uptime:** {}\n".format(self.get_uptime())
    info += "**\u3164\u25A0 Servers:** {:,} ({:,} users)\n".format(len(bot.guilds), len(bot.users))
    info += "\nWant y'shtola on _your_ server? [Click here](https://discordapp.com/api/oauth2/authorize?client_id=547516876851380293&permissions=1861483585&scope=bot).\n"
    info += "Like this bot? [Consider donating a dollar or two](https://www.patreon.com/yshtolabot)."

    embed.add_field(name ="**__Bot Statistics__**", value = info)
    embed.set_footer(text = "Use {}help to produce a list of commands".format(ctx.prefix))
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


  # :b: emoji
  @commands.command(description = ":b:")
  async def b(self, ctx, *, input: str = None):
    if input is None:
      await ctx.send(embed = discord.Embed(title = "", description = "Try using `{}b <words>`".format(ctx.prefix)))
      return
    new_line = ""
    for character in input:
      new_line += ":b:" if character in "bp" or (character.isalpha() and character not in "aeioug" and randint(1, 10) == 10) else character
    new_line.replace("gg", ":b::b:")
    await ctx.send(embed = discord.Embed(title = "", description = "{}\n{}".format(ctx.author.mention, new_line), color = ctx.author.color))


  # prints out a list of commands
  @commands.command(hidden = True, description = "Prints a list of commands and what they do")
  async def help(self, ctx, *, cog_name: str = ""):
    embed = discord.Embed(title = "**Help Menu**")
    if cog_name.title() in bot.cogs:
      self.get_list_of_commands(embed, cog_name)
    else:
      output = ""
      for cogs in bot.cogs:
        output += "**{}**\n".format(cogs)
      embed.add_field(name = "__**Cogs**__", value = output)
    embed.set_footer(text = "No prefix is required when speaking to me through direct messages.")
    await ctx.author.send(embed = embed)


  # helper method for getting desc of commands
  def get_list_of_commands(self, embed, cog_name):
    command_text = ""
    if cog_name.title() in bot.cogs:
      for command in bot.get_cog(cog_name.title()).get_commands():
        desc = command.description
        if desc == "":
          desc = "Description not provided."
        if not command.hidden:
          if not (desc.endswith(".") or desc.endswith("!")):
            desc += "."
          command_text += "**\u3164\u25A0 {}:** {}\n".format(str(command).replace("_", ""), desc)
      if command_text != "":
        embed.add_field(name = "__Commands in **{}**__".format(cog_name.lower()), value = command_text, inline = False)
      else:
        embed.add_field(name = "__Huh? It's empty here...__", value = "It looks like all of the commands here are not for you...")


def setup(bot):
  bot.add_cog(General(bot))