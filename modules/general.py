import discord
from discord.ext import commands
from builtins import bot
from modules.utils import user_json
from random import randint

class General(commands.Cog):
  def __init__(self, bot):
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

  # repeats a message
  @commands.command(aliases = ["me", "say"], description = "Repeats a given message.")
  async def echo(self, ctx, *, message):
    await ctx.send(embed = discord.Embed(title = "", description = message, color = ctx.author.color))


  # makes bot react to a message
  @commands.is_owner()
  @commands.command(description = "Adds a reaction to a given message.")
  async def addreaction(self, ctx, msg_id, emoji):
    msg = await ctx.fetch_message(int(msg_id))
    try:
      await msg.add_reaction(str(emoji))
    except:
      await ctx.send(embed = discord.Embed(title = "**Error!**", description = "{} is not a valid emoji.".format(emoji)))


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
    self.top_five(embed, 'level', 'Highest Levels')
    self.top_five(embed, 'item_level', 'Mightiest Item Levels')
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
    embed.add_field(name = "**__{}__**".format(title), value = top_users, inline = False)


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
      new_line += ":b:" if character in "bp" or (character.isalpha() and character not in "aeioug" and randint(1, 4) == 4) else character
    new_line.replace("gg", ":b::b:")
    await ctx.send(embed = discord.Embed(title = "", description = "{}\n{}".format(ctx.author.mention, new_line), color = ctx.author.color))


  # color picker
  @commands.command(description = "Returns some data about a specified color. Leave color blank to get a random color.")
  async def color(self, ctx, *, input: str = None):
    if input is None:
      r = lambda: randint(0,255)
      input_color = '%02x%02x%02x' % (r(),r(),r())
      await ctx.send(input_color)

  # prints out a list of commands
  @commands.command(hidden = True, description = "Prints a list of commands and what they do")
  async def help(self, ctx, *, cog_name: str = ""):
    embed = discord.Embed(title = "**Help Menu**", description = "Type `!help <cog_name>` to get a list of commands.")
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