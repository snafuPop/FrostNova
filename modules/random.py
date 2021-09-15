import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids

from random import randint
from random import choice

class Random(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # rolls a random number between 1 and a user defined max (defaults to 100)
  # also optionally takes in a string input
  @cog_ext.cog_slash(name = "roll", description = "Rolls a dice.", guild_ids = guild_ids, 
    options = [create_option(
      name = "number",
      description = "The highest possible number you can roll. Leave blank for 100.",
      option_type = 4,
      required = False),
    create_option(
      name = "declaration",
      description = "Attaches a declaration to your outcome.",
      option_type = 3,
      required = False)]
    )
  async def roll(self, ctx, number: int = 100, declaration: str = ""):
    if number <= 1:
      await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: Maybe roll a value greater than 1, {}? (｀Д´)".format(ctx.author.mention)))
      return

    # rolls a bonus modifier that determines the appearance of special dice or not
    dice = ":diamond_shape_with_a_dot_inside:" if 1 == randint(1,1000000) else ":game_die:"

    # creates the embed message
    result = randint(1, number)
    embed = discord.Embed(title = "", description = "{} {} rolled a **{:,}**! {}".format(dice, ctx.author.mention, result, dice), color = ctx.author.color)
    embed.set_footer(text = "...out of {:,}".format(number))

    # parses the declaration
    if declaration != "":
      declaration = "\"" + declaration + "\""
      embed.set_author(name = declaration, icon_url = ctx.author.avatar_url)
    
    await ctx.send(embed=embed)


  @cog_ext.cog_slash(name = "coinflip", description = "Flips a coin.", guild_ids = guild_ids)
  async def flip(self, ctx):
    rand = randint(1, 101)
    if rand == 1:
      result = "its side"
    elif rand >= 51:
      result = "tails"
    else:
      result = "heads"  
    embed = discord.Embed(description="{} flipped a coin and it landed on **{}**!".format(ctx.author.mention, result), color = ctx.author.color)
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Random(bot))