import discord
from discord.ext import commands
from builtins import bot

from random import choice
from googletrans import Translator

translator = Translator()

def makeColor():
  # genereates a random color  
  colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
  colour = int(colour, 16)
  return colour

@bot.command(pass_context = True, description = "Translates given text")
async def translate(ctx, language: str = None, *, text: str = None):
  if text is None:
    embed = discord.Embed(title = "", description = "Try translating text using `!translate <target language> <text>`.")
  else: 
    language = language[:2]
    output = translator.translate(text, dest = language)

    embed = discord.Embed(title = output.text, description = "Translated for {}.".format(ctx.message.author.mention), color = makeColor())

    if output.pronunciation is not None:
      embed.add_field(name = "Pronunciation:", value = output.pronunciation)
      
    embed.set_footer(text = "Original text: {}".format(text))
  await bot.say(embed = embed)