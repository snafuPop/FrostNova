import discord
from discord import app_commands
from discord.ext import commands

from PIL import ImageDraw, Image, ImageFont
from io import BytesIO
import textwrap
import os


class Meme_Template():
  def __init__(self, image_name, font_name, font_size, message, coords, color):
    self.image_name = image_name
    self.font_name = font_name
    self.font_size = font_size
    self.message = message
    self.coords = coords
    self.color = color


  def make_image(self):
    image_filepath = os.path.dirname(__file__) + "/_images/"
    font_filepath = os.path.dirname(__file__) + "/_data/"

    with Image.open(image_filepath + self.image_name) as image:
      draw = ImageDraw.Draw(image)
      font = ImageFont.truetype(font_filepath + self.font_name, self.font_size)
      draw.text(tuple(self.coords), self.message, tuple(self.color), font = font)

      output_buffer = BytesIO()
      image.save(output_buffer, "png")
      output_buffer.seek(0)
    return output_buffer


class Image_Preach(Meme_Template):
  def __init__(self, message):
    super().__init__("jesus.png", "FantasqueSansMono-Regular.ttf", 25, message, [165, 175], [0, 0, 0, 255])


class Image_Sans(Meme_Template):
  def __init__(self, message):
    super().__init__("sans.png", "UndertaleSans.ttf", 24, message, [117, 30], [255, 255, 255, 255])


class Meme(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  meme = app_commands.Group(name = "meme", description = "Generates a meme with a specified message")

  @meme.command(name = "preach", description = "Preach some truth")
  @app_commands.describe(message = "Some truth to preach")
  async def preach(self, interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    message = textwrap.fill(message, width = 14)
    image_file = Image_Preach(message).make_image()
    await interaction.followup.send(file = discord.File(fp = image_file, filename = "jesus.png"))


  @meme.command(name = "sans", description = "uhuhuhuhuhuhuhuh")
  @app_commands.describe(message = "Any message")
  async def sans(self, interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    message = textwrap.fill(message, width = 30)
    image_file = Image_Sans(message).make_image()
    await interaction.followup.send(file = discord.File(fp = image_file, filename = "sans.png"))


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Meme(bot))