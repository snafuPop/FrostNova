import discord
from discord.ext import commands
from builtins import bot

from random import choice
from googletrans import Translator

translator = Translator()

class Translate(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context = True, description = "Translates given text")
  async def translate(self, ctx, language: str = None, *, text: str = None):
    if text is None:
      embed = discord.Embed(title = "", description = "Try translating text using `!translate <target language> <text>`.")
    else: 
      language = language[:2]
      output = translator.translate(text, dest = language)

      embed = discord.Embed(title = output.text, description = "Translated for {}.".format(ctx.author.mention), color = ctx.author.color)

      if output.pronunciation is not None:
        embed.add_field(name = "Pronunciation:", value = output.pronunciation)
        
      embed.set_footer(text = "Original text: {}".format(text))
    await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(Translate(bot))