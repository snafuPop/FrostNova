import discord
from discord.ext import commands
from builtins import bot
import urllib.parse
from random import choice
from googletrans import Translator
import aiohttp

translator = Translator()

class Language(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(description = "Translates given text")
  async def translate(self, ctx, language: str = None, *, text: str = None):
    if text is None:
      embed = discord.Embed(title = "", description = "Try translating text using `{}translate <target language> <text>`, {}.".format(ctx.prefix, ctx.author.mention))
    else:
      language = language[:2]
      output = translator.translate(text, dest = language)

      embed = discord.Embed(title = output.text, description = "Translated for {}.".format(ctx.author.mention), color = ctx.author.color)

      if output.pronunciation is not None:
        embed.add_field(name = "Pronunciation:", value = output.pronunciation)

      embed.set_footer(text = "Original text: {}".format(text))
    await ctx.send(embed = embed)

  @commands.command(aliases = ["jp"], description = "Looks up a word on Jisho.org")
  async def jisho(self, ctx, term: str = None, max_entries: int = 1):
    if term is None:
      embed = discord.Embed(title = "", description = "Try searching a word on Jisho using `{}jisho <word> <number of entries>`, {}".format(ctx.prefix, ctx.author.mention))
    else:
      url = "http://jisho.org/api/v1/search/words?keyword=" + urllib.parse.quote(term, encoding = "utf-8")
      try:
          async with aiohttp.ClientSession() as session:
              async with session.get(url) as response:
                  data = await response.json()
      except Exception as error:
          await ctx.send(embed = discord.Embed(title = "", description = "Request failed: {}".format(error)))
          return

      results = data["data"]
      if not results:
          await ctx.send(embed = discord.Embed(title = "No results found", description = ctx.author.mention))
          return

      embed = discord.Embed(title = "Results for \"{}\"".format(term), description = "Requested by {}".format(ctx.author.mention), color = ctx.author.color)
      embed.set_thumbnail(url = "https://pbs.twimg.com/profile_images/378800000741890744/43702f3379bdb7d0d725b70ae9a5bd59_400x400.png")

      # keeps track of entry counts
      count = 1

      # reduce the number of entries
      if 5 <= max_entries:
        max_entries = 5
      if len(results) <= max_entries:
        max_entries = len(results)

      # iterating through each entry
      for entries in results[:max_entries]:

        # string used to store definitions and particles
        info = ""

        # grabbing kanji and hiragana
        if "word" in entries["japanese"][0]:
          word = entries["japanese"][0]["word"]
          reading = "（" + entries["japanese"][0]["reading"] + "）"
        else:
          word = ""
          reading = entries["japanese"][0]["reading"]

        # grabbing all definitions and particles
        entry_list = []
        last_particle = ""
        for entry in entries["senses"]:
          single_entry = []

          # sometimes particles are null, meaning they adopt the previous, non-blank particle
          if entry["parts_of_speech"]:
            particle = ", ".join(entry["parts_of_speech"])
            single_entry.append(particle)
            last_particle = particle
          else:
            single_entry.append(last_particle)

          # combining definitions
          single_entry.append("; ".join(entry["english_definitions"]))
          entry_list.append(single_entry)

        # storing it into info
        for entry in entry_list:
          info += "\n\u3164 **{}:** {}".format(entry[0], entry[1])

        # adding a link to the actual jisho page
        info += "\n\u3164 [More Information](https://jisho.org/word/{})".format(word)

        # formally adding it to a field
        embed.add_field(name = "**{}.** {} {}".format(count, word, reading), value = info, inline = False)
        count += 1

    await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Language(bot))