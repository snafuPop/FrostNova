import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from builtins import bot
from PIL import ImageDraw, Image, ImageFont
from io import BytesIO
import textwrap

class Memeify(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.filepath = '/yvona/modules/'


  def get_image_filepath(self):
    return self.filepath + '_images/'


  def get_font_filepath(self):
    return self.filepath + '_data/'


  # controls making all of the images via PIL and running it thorugh BytesIO to make Discord happy
  def make_image(self, image_name, message, coords, color, font_name, font_size):
    with Image.open(self.get_image_filepath() + image_name) as image:
      draw = ImageDraw.Draw(image)
      font = ImageFont.truetype(self.get_font_filepath() + font_name, font_size)
      draw.text((coords[0], coords[1]), message, (color[0], color[1], color[2], color[3]), font = font)

      output_buffer = BytesIO()
      image.save(output_buffer, "png")
      output_buffer.seek(0)
    return output_buffer


  @cog_ext.cog_subcommand(base = "meme", name = "badcode", description = "Make fun of some code.", 
    options = [create_option(
      name = "code",
      description = "The code to make fun of.",
      option_type = 3,
      required = True)])
  async def badcode(self, ctx, *, code:str = None):
    await ctx.defer()
    code = code.replace("`", "")
    await ctx.send(file = discord.File(fp = self.make_image("comsci.png", code, [430, 25], [0, 0, 0, 255], "FantasqueSansMono-Regular.ttf", 20), filename = "badcode.png"))


  @cog_ext.cog_subcommand(base = "meme", name = "preach", description = "Preach some truth, even if they hate the truth.",
    options = [create_option(
      name = "truth", 
      description = "The hard truth to preach.", 
      option_type = 3, 
      required = True)])
  async def preach(self, ctx, *, truth: str = None):
    await ctx.defer()
    truth = textwrap.fill(truth, width = 14)
    await ctx.send(file = discord.File(fp = self.make_image("jesus.png", truth, [165, 175], [0, 0, 0, 255], "FantasqueSansMono-Regular.ttf", 25), filename = "jesus.png"))
  

  @cog_ext.cog_subcommand(base = "meme", name = "sans", description = "uhuhuhuhuhuhuhuh", 
    options = [create_option(
      name = "message",
      description = "Any message.",
      option_type = 3,
      required = True)])
  @commands.command(description = "uhuhuhuhuhuhuhuh")
  async def sans(self, ctx, *, message: str = None):
    await ctx.defer()
    message = textwrap.fill(message, width = 30)
    await ctx.send(file = discord.File(fp = self.make_image("sans.png", message, [117, 30], [255, 255, 255, 255], "UndertaleSans.ttf", 24), filename = "sans.png"))
    

def setup(bot):
  bot.add_cog(Memeify(bot))