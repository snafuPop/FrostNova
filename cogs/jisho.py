import discord
from discord import app_commands
from discord.ext import commands

import typing
import Paginator
import aiohttp
import jisho_api
from jisho_api.word import Word
from jisho_api.kanji import Kanji
from jisho_api.sentence import Sentence

from cogs.utils.keywords import Keyword as ky


class Jisho(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.jisho_thumbnail_url = "https://pbs.twimg.com/profile_images/378800000741890744/43702f3379bdb7d0d725b70ae9a5bd59_400x400.png"


  def append_info_to_embed(self, embed: discord.Embed, interaction: discord.Interaction, search_term: str):
      embed.set_author(name = f"Results for \"{search_term}\"", icon_url = interaction.user.display_avatar.url)
      embed.set_footer(text = "Powered by jisho.org", icon_url = self.jisho_thumbnail_url)


  jisho = app_commands.Group(name = "jisho", description = "Commands that involve searching jisho.org")

  @jisho.command(name = "word", description = "Searches a word on jisho.org")
  @app_commands.describe(term = "The term to search.", results = "The number of results you'd like back (defaults to at most 3)")
  async def get_word_from_jisho(self, interaction: discord.Interaction, term: str, results: typing.Optional[app_commands.Range[int, 1]] = 3):
    jisho_request = None
    try:
      jisho_request = Word.request(term)
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
      await interaction.response.send_message(embed = embed)
      return

    if not jisho_request:
      embed = self.bot.create_error_response(message = f"No results for \"{term}\" were found")
      await interaction.response.send_message(embed = embed)
      return

    jisho_data = jisho_request.dict()['data']
    jisho_entries = min(len(jisho_data), results)
    jisho_data = jisho_data[:jisho_entries]

    embeds = []
    for entry in jisho_data:
      word = entry['japanese'][ 0] if isinstance(entry['japanese'], list) else entry['japanese']
      title = f"{word['word']} ({word['reading']})"

      tags = entry['tags']
      description = ", ".join(["#" + tag for tag in tags]) if tags else None
      embed = discord.Embed(title = title, description = description, url = f"https://jisho.org/word/{entry['slug']}", color = interaction.user.color)

      definitions = ""
      counter = 1

      for sense in entry['senses']:
        definitions += f"**{counter}.** *{sense['parts_of_speech'][0]}:* {'; '.join(sense['english_definitions'])}\n"
        counter += 1

      embed.add_field(name = "**Defintion(s):**", value = definitions)
      self.append_info_to_embed(embed, interaction, term)
      embeds.append(embed)

    await self.bot.create_paginated_embed().start(interaction, pages = embeds)


  @jisho.command(name = "kanji", description = "Pulls up information about a kanji character on jisho.org")
  @app_commands.describe(kanji = "The kanji you'd like to find information about")
  async def get_kanji_from_jisho(self, interaction: discord.Interaction, kanji: app_commands.Range[str, 1, 1]):
    jisho_request = None
    try:
      jisho_request = Kanji.request(kanji)
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
      await interaction.response.send_message(embed = embed)
      return

    if not jisho_request:
      embed = self.bot.create_error_response(message = f"No results for \"{kanji}\" were found")
      await interaction.response.send_message(embed = embed)
      return

    jisho_data = jisho_request.dict()['data']

    main_meanings = ", ".join(jisho_data['main_meanings'])
    title = f"{jisho_data['kanji']}: {main_meanings}"

    kun_readings = jisho_data['main_readings']['kun']
    on_readings = jisho_data['main_readings']['on']
    kun = ", ".join(kun_readings) if kun_readings else "None"
    on = ", ".join(on_readings) if on_readings else "None"
    strokes = jisho_data['strokes']
    embed = discord.Embed(title = title, description = f"**kun:** {kun}\n**on:** {on}\n**Strokes:** {strokes}", color = interaction.user.color)

    radical_meaning = jisho_data['radical']['meaning']
    radical_parts = " ".join(jisho_data['radical']['parts'])
    embed.add_field(name = "**__Radical(s):__**", value = f"**Meaning:** {radical_meaning}\n**Parts:** {radical_parts}", inline = False)

    reading_examples = jisho_data['reading_examples']

    def get_reading_examples(examples, reading_type: str):
      examples = ""
      for example in reading_examples[reading_type]:
        examples += f"**{example['kanji']} ({example['reading']}):** {', '.join(example['meanings'])}\n"
      return examples

    if reading_examples['kun']:
      value = get_reading_examples(reading_examples, 'kun')
      embed.add_field(name = "**__Kunyomi Readings:__**", value = value)
    
    if reading_examples['on']:
      value = get_reading_examples(reading_examples, 'on')
      embed.add_field(name = "**__Onyomi Readings__**", value = value)

    self.append_info_to_embed(embed, interaction, kanji)
    await interaction.response.send_message(embed = embed)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Jisho(bot))