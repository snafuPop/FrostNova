import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from builtins import bot, guild_ids

from random import random
from random import randint
from random import choice
from titlecase import titlecase

class Witchy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.major_arcana = ["the fool", "the magician", "the high priestess", "the empress", "the emperor", "the hierophant", "the lovers", "the chariot", "strength", "the hermit", "wheel of fortune", "justice", "the hanged man", "death", "temperance", "the devil", "the tower", "the star", "the moon", "the sun", "judgement", "the world"]
    self.minor_arcana = self.create_deck()

  def create_deck(self):
    deck = []
    card_type = ["cups", "swords", "wands", "pentacles"]
    card_num = ["king", "queen", "knight", "page", "ten", "nine", "eight", "seven", "six", "five", "four", "three", "two", "ace"]
    for a_type in card_type:
      for a_num in card_num:
        deck.append(a_num + " of " + a_type)
    return deck

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

  def get_card(self):
    spread = []
    spread.append(choice(self.major_arcana))

    # appends 3 random minor arcana
    minor_arcana = self.minor_arcana
    for i in range (3):
      spread.append(minor_arcana.pop(randint(0,len(minor_arcana))))

    return spread

  @cog_ext.cog_slash(name = "8ball", description = "Ask the mystical 8ball a question.", guild_ids = guild_ids, 
    options = [create_option(
      name = "question",
      description = "Your question.",
      option_type = 3,
      required = True)])
  async def _8ball(self, ctx, question: str = None):
    reading = self.get_8ball()
    embed = discord.Embed(title = "", description = ":8ball: {}".format(reading[1]), color = reading[0])
    embed.set_author(name = "\"{}\"".format(question), icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)


  @cog_ext.cog_slash(name = "tarot", description = "Generates a spread of tarot cards.")

  @commands.command(description = "Generates a spread of tarot cards.")
  async def tarot(self, ctx):
    '''Returns a major arcana and 3 minor arcana.'''

    # grabs the spread
    spread = self.get_card()

    embed = discord.Embed(title="", description="{}'s spread...".format(ctx.author.mention), color = ctx.author.color)
    embed.add_field(name="Major Arcana", value="[{}](https://www.trustedtarot.com/cards/{})".format(titlecase(spread[0]), spread[0].replace(" ", "-")), inline=False)
    embed.set_thumbnail(url="https://www.trustedtarot.com/img/cards/{}.png".format(spread[0].replace(" ", "-")))
    embed.add_field(name="Minor Arcanas", value="[The {}](https://www.trustedtarot.com/cards/{}), [The {}](https://www.trustedtarot.com/cards/{}), and [The {}](https://www.trustedtarot.com/cards/{})".format(titlecase(spread[1]), spread[1].replace(" ", "-"), titlecase(spread[2]), spread[2].replace(" ", "-"), titlecase(spread[3]), spread[3].replace(" ", "-")))
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Witchy(bot))