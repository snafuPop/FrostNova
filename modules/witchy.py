import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from ButtonPaginator import Paginator
from discord.ext import commands
from builtins import bot, guild_ids

import random
from random import randint
from random import choice
from titlecase import titlecase

import aiohttp

class Witchy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @cog_ext.cog_slash(name = "tarot", description = "Generates a spread of tarot cards.", guild_ids = guild_ids)
  async def tarot(self, ctx):
    await ctx.defer()
    try:
      url = "https://rws-cards-api.herokuapp.com/api/v1/cards/random?n=5"
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          spread = await response.json()
    except Exception as error:
      await ctx.send(embed = discord.Embed(title = (str(type(error).__name)), description = ":no_entry: " + str(error)))
      return

    questions = ["What is happening in this moment?", "How can I weather it easily and with grace?", "What is the lesson?", "What is leaving at this time?", "What is arriving at this time?"]
    embeds = []
    question_index = 0

    for card in spread["cards"]:
      is_reversed = bool(random.getrandbits(1))
      is_major = card["type"] == "major"

      if is_major:
        card_name = "The Reversed {}".format(card["name"][4:]) if is_reversed else card["name"]
      else:
        card_name = "Reversed {}".format(card["name"]) if is_reversed else card["name"]

      card_meaning = card["meaning_rev"] if is_reversed else card["meaning_up"]

      embed = discord.Embed(title = card_name, description = "{} Arcana".format(titlecase(card["type"])), color = ctx.author.color)
      embed.add_field(name = "**{}**".format(questions[question_index]), value = "{}".format(card_meaning))
      embed.set_thumbnail(url = "https://www.trustedtarot.com/img/cards/{}.png".format(card["name"].replace(" ", "-").lower()))
      embeds.append(embed)
      question_index += 1

    paginated_embed = Paginator(bot = self.bot, ctx = ctx, embeds = embeds, only = ctx.author)
    await paginated_embed.start()


  def get_8ball(self):
    # returns a random 8-ball response and a color representing its polarity

    ball = {
      "good": ["It is certain", "It is decidedly so", "Without a doubt", "Yes — definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes"],
      "neutral": ["Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again"],
      "bad": ["Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
    }

    # gets a random key (polarity)
    polarity = choice(list(ball))

    # gets a random reading
    reading = choice(ball[polarity])

    # determines a color based on polarity
    if polarity == "good":
      polarity = 0x2ecc71
    if polarity == "neutral":
      polarity = 0xf1c40f
    if polarity == "bad":
      polarity = 0xe74c3c

    return [polarity, reading]


  @cog_ext.cog_slash(name = "8ball", description = "Ask the mystical 8ball a question.", guild_ids = guild_ids, 
    options = [create_option(
      name = "question",
      description = "Your question.",
      option_type = 3,
      required = True)])
  async def _8ball(self, ctx, question: str = None):
    reading = self.get_8ball()
    if not question.endswith('?'):
      question = question + "?"

    embed = discord.Embed(title = "", description = ":8ball: {}".format(reading[1]), color = reading[0])
    embed.set_author(name = "\"{}\"".format(question), icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)



def setup(bot):
  bot.add_cog(Witchy(bot))