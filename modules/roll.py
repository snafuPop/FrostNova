import discord
from discord.ext import commands
from builtins import bot

from random import randint
from random import choice

def makeColor():
  # genereates a random color  
  colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
  colour = int(colour, 16)
  return colour

@bot.command(pass_context = True, description = "Generates a random number from 1 to a defined number (by default 100)")
async def roll(ctx, number: int = 100, *, request: str = ""):
  # rolls a random number between 1 and a user defined max (defaults to 100)
  # also optionally takes in a string input

  if number <= 1:
    embed = discord.Embed(title="", description="Maybe roll a value greater than 1, {}? (｀Д´)".format(ctx.message.author.mention), color=makeColor())

  else:
    result = randint(1, number)

    # rolls a bonus modifier that determines the appearance of special dice or not
    bonus = randint(1,1000000)
    if bonus == 1:
      dice = ":diamond_shape_with_a_dot_inside:"
    else:
      dice = ":game_die:"

    # parses the request
    if request is not "":
      request = "\"" + request + "\""

    # creates the embed message
    embed = discord.Embed(title=request, description="{} {} rolled a **{:,}**! {}".format(dice, ctx.message.author.mention, result, dice), color=makeColor())
    embed.set_footer(text="...out of {:,}.".format(number))
  
  # sends the message
  await bot.say(embed=embed)

@bot.command(pass_context = True, description = "Flips a coin")
async def flip(ctx):
  # flips a coin
  # has a 100/101 chance of being heads or tails, and a 1/100 chance of landing on its side

  rand = randint(1, 101)

  if rand == 1:
    result = "its side"
  elif rand >= 51:
    result = "tails"
  else:
    result = "heads"

  embed = discord.Embed(description="{} flipped a coin and it landed on **{}**!".format(ctx.message.author.mention,result), color=makeColor())
  await bot.say(embed=embed)