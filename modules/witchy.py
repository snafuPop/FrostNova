import discord
from discord.ext import commands
from builtins import bot

from random import random
from random import randint
from random import choice
from titlecase import titlecase

class Witchy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

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
    if polarity is "good":
      polarity = 0x2ecc71
    if polarity is "neutral":
      polarity = 0xf1c40f
    if polarity is "bad":
      polarity = 0xe74c3c

    return [polarity, reading]

  def get_card(self):
    # returns a random major arcana and 3 random minor arcana

    spread = []
    major_arcana = ["the fool", "the magician", "the high priestess", "the empress", "the emperor", "the hierophant", "the lovers", "the chariot", "strength", "the hermit", "wheel of fortune", "justice", "the hanged man", "death", "temperance", "the devil", "the tower", "the star", "the moon", "the sun", "judgement", "the world"]
    minor_arcana = ["king of cups", "queen of cups", "knight of cups", "page of cups", "ten of cups", "nine of cups", "eight of cups", "seven of cups", "six of cups", "five of cups", "four of cups", "three of cups", "two of cups", "ace of cups", "king of swords", "queen of swords", "knight of swords", "page of swords", "ten of swords", "nine of swords", "eight of swords", "seven of swords", "six of swords", "five of swords", "four of swords", "three of swords", "two of swords", "ace of swords", "king of wands", "queen of wands", "knight of wands", "page of wands", "ten of wands", "nine of wands", "eight of wands", "seven of wands", "six of wands", "five of wands", "four of wands", "three of wands", "two of wands", "ace of wands", "king of pentacles", "queen of pentacles", "knight of pentacles", "page of pentacles", "ten of pentacles", "nine of pentacles", "eight of pentacles", "seven of pentacles", "six of pentacles", "five of pentacles", "four of pentacles", "three of pentacles", "two of pentacles", "ace of pentacles"]

    # appends major arcana
    spread.append(choice(major_arcana))

    # appends 3 random minor arcana
    for i in range (3):
      spread.append(minor_arcana.pop(randint(0,len(minor_arcana))))

    return spread

  @commands.command(aliases = ["8ball"], description = "Generates a standard 8ball response.")
  async def _8ball(self, ctx, *, question: str = None):
    '''Reads in a question and returns a standard 8-Ball response.'''

    if question is None:
      # catches empty responses
      embed = discord.Embed(title = "", description = "Try asking a question with `!8ball <question>`, {}".format(ctx.author.mention), color = 0xe74c3c)
    else:
      # fetches a response
      reading = self.get_8ball()

      embed = discord.Embed(title=question, description="{}, {}.".format(reading[1], ctx.author.mention), color = reading[0])
    await ctx.send(embed = embed)

  @commands.command(pass_context = True, description = "Generates a spread of tarot cards.")
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