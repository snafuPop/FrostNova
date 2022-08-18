import discord
from discord import app_commands
from discord.ext import commands

from random import randint, choice, getrandbits
from enum import Enum
import Paginator
import aiohttp

from cogs.utils.keywords import Keyword as ky


class EightBall():
  def __init__(self):
    self.messages = {
      "good": ["It is certain", "It is decidedly so", "Without a doubt", "Yes — definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes"],
      "neutral": ["Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again"],
      "bad": ["Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
    }


  def get_message(self):
    polarity = choice(list(self.messages))
    reading = choice(self.messages[polarity])
    polarity_color = self.get_polarity_color(polarity)
    return reading, polarity_color


  def get_polarity_color(self, key):
    match key:
      case "good":
        return 0x2ecc71
      case "neutral":
        return 0xf1c40f
      case "bad":
        return 0xe74c3c
    

class Random(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.eightball = EightBall()


  @app_commands.command(name = "roll", description = "Roll some dice!")
  @app_commands.describe(max_number = "The highest number that you can roll", declaration = "A string of text that you can attach to your dice roll")
  async def rolldice(self, interaction: discord.Interaction, max_number: int = 100, declaration: str = None):
    if max_number <= 1:
      message = "Maybe roll a value greater than 1? (｀Д´)"
      embed = self.bot.create_error_response(message = message)
      await interaction.response.send_message(embed = embed, ephemeral = True)
      return

    dice_icon = "diamond_shape_with_a_dot_inside:" if 1 == randint(1,1000000) else ":game_die:"

    result = randint(1, max_number)
    message = f"{dice_icon} {interaction.user.mention} rolled a **{result:,}**!"
    embed = discord.Embed(title = "", description = message, color = interaction.user.color)

    if declaration:
      declaration = f"\"{declaration}\""
      embed.set_author(name = declaration, icon_url = interaction.user.display_avatar.url)

    embed.set_footer(text = f"...out of {max_number:,}")
    await interaction.response.send_message(embed = embed)


  @app_commands.command(name = "coinflip", description = "Flip a coin!")
  async def coinflip(self, interaction: discord.Interaction):
    random_num = randint(0,101)
    if random_num == 0:
      result = "its side"
    elif random_num <= 51:
      result = "tails"
    else:
      result = "heads"

    message = f":coin: {interaction.user.mention} flipped a coin and it landed on **{result}**!"
    embed = discord.Embed(title = "", description = message, color = interaction.user.color)
    await interaction.response.send_message(embed = embed)


  @app_commands.command(name = "choose", description = "Chooses one thing from a list")
  @app_commands.describe(choices = "A list of choices, with each separated by a semicolon (;)")
  async def choose(self, interaction: discord.Interaction, choices: str):
    if choices.endswith(";"):
      choices = choices[:-1]

    choices_list = list(set(choices.split(";")))
    if len(choices_list) <= 1:
      message = "You need to provide more than one choice"
      embed = self.bot.create_error_response(message = message)
      embed.add_field(name = "For example:", value =  "`\\choose vanilla;strawberry;chocolate`")
      await interaction.response.send_message(embed = embed)
      return

    chosen_item = choice(choices_list)
    description = f":point_right: I choose **{chosen_item}**!"
    embed = discord.Embed(title = "", description = description)

    oxford_comma = " and " if len(choices_list) == 2 else ", and "
    choices_as_sentence = ", ".join(choices_list[:-1]) + oxford_comma + choices_list[len(choices_list) - 1]
    embed.set_footer(text = f"...out of {choices_as_sentence}")
    await interaction.response.send_message(embed = embed)



  @app_commands.command(name = "8ball", description = "Ask the mystical 8-Ball a question!")
  @app_commands.describe(question = "A question that you can attach to your 8-Ball reading")
  async def eightball(self, interaction: discord.Interaction, question: str):
    reading, polarity_color = self.eightball.get_message()
    embed = discord.Embed(title = "", description = f":8ball: *{reading}*", color = polarity_color)

    if not question.endswith('?'):
      question += '?'
    embed.set_author(name = f"\"{question}\"", icon_url = interaction.user.display_avatar.url)
    await interaction.response.send_message(embed = embed)



  @app_commands.command(name = "tarot", description = "Draw a spread of tarot cards!")
  async def tarot(self, interaction: discord.Interaction):
    try:
      url = "https://rws-cards-api.herokuapp.com/api/v1/cards/random?n=5"
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          tarot_spread = await response.json()
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
      await interaction.response.send_message(embed = embed)
      return

    questions = [
      "What is happening in this moment?", 
      "How can I weather it easily and with grace?", 
      "What is the lesson?", 
      "What is leaving at this time?", 
      "What is arriving at this time?"]

    embeds = []

    for card in tarot_spread['cards']:
      is_reversed = bool(getrandbits(1))
      is_major = card['type'] == "major"

      if is_major:
        card_name = f"The Reversed {card['name'][4:]}" if is_reversed else card['name']
      else:
        card_name = f"Reversed {card['name']}" if is_reversed else card['name']

      card_meaning = card['meaning_rev'] if is_reversed else card['meaning_up']

      embed = discord.Embed(title = card_name, description = f"{card['type'].title()} Arcana", color = interaction.user.color)
      embed.add_field(name = f"{questions.pop(0)}", value = card_meaning)
      embed.set_thumbnail(url = f"https://www.trustedtarot.com/img/cards/{card['name'].replace(' ', '-').lower()}.png")
      embeds.append(embed)

    await Paginator.Simple().start(interaction, pages = embeds)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Random(bot))