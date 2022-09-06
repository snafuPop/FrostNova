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
    await interaction.followup.send(file = discord.File(fp = image_file, filename = "jesus.png"))


  # # controls making all of the images via PIL and running it thorugh BytesIO to make Discord happy
  # def make_image(self, image_name, message, coords, color, font_name, font_size):
  #   with Image.open(self.get_image_filepath() + image_name) as image:
  #     draw = ImageDraw.Draw(image)
  #     font = ImageFont.truetype(self.get_font_filepath() + font_name, font_size)
  #     draw.text((coords[0], coords[1]), message, (color[0], color[1], color[2], color[3]), font = font)

  #     output_buffer = BytesIO()
  #     image.save(output_buffer, "png")
  #     output_buffer.seek(0)
  #   return output_buffer


  # @cog_ext.cog_subcommand(base = "meme", name = "badcode", description = "Make fun of some code.", 
  #   options = [create_option(
  #     name = "code",
  #     description = "The code to make fun of.",
  #     option_type = 3,
  #     required = True)])
  # async def badcode(self, ctx, *, code:str = None):
  #   await ctx.defer()
  #   code = code.replace("`", "")
  #   await ctx.send(file = discord.File(fp = self.make_image("comsci.png", code, [430, 25], [0, 0, 0, 255], "FantasqueSansMono-Regular.ttf", 20), filename = "badcode.png"))




  # @cog_ext.cog_subcommand(base = "meme", name = "sans", description = "uhuhuhuhuhuhuhuh", 
  #   options = [create_option(
  #     name = "message",
  #     description = "Any message.",
  #     option_type = 3,
  #     required = True)])
  # @commands.command(description = "uhuhuhuhuhuhuhuh")
  # async def sans(self, ctx, *, message: str = None):
  #   await ctx.defer()
  #   message = textwrap.fill(message, width = 30)
  #   await ctx.send(file = discord.File(fp = self.make_image("sans.png", message, [117, 30], [255, 255, 255, 255], "UndertaleSans.ttf", 24), filename = "sans.png"))
    

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Meme(bot))