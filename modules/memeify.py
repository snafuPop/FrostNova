import discord
from discord.ext import commands
from builtins import bot
from PIL import ImageDraw, Image, ImageFont
from io import BytesIO
import textwrap

class Memeify(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # controls making all of the images via PIL and running it thorugh BytesIO to make Discord happy
  def make_image(self, image_name, message, coords, color, font_name, font_size):
    with Image.open("/home/snafuPop/yshtola/modules/_images/" + image_name) as image:
      draw = ImageDraw.Draw(image)
      font = ImageFont.truetype("/home/snafuPop/yshtola/modules/_data/" + font_name, font_size)
      draw.text((coords[0], coords[1]), message, (color[0], color[1], color[2], color[3]), font = font)

      output_buffer = BytesIO()
      image.save(output_buffer, "png")
      output_buffer.seek(0)
    return output_buffer

  @commands.command(aliases = ["horrorcode", "comsci", "code"], description = "Hightlight some bad code.")
  async def badcode(self, ctx, *, message:str = None):
    if message is None:
      await ctx.send(embed = discord.Embed(title = "", description = "You can show off some truly awful code using `{}badcode <text>`.".format(ctx.prefix)))
      return

    if message.startswith("```"):
      message = message.replace("```", "")
      message = message.split("\n", 1)[1]
      
    await ctx.send(file = discord.File(fp = self.make_image("comsci.png", message, [430,25], [0,0,0,255], "FantasqueSansMono-Regular.ttf", 20), filename = "badcode.png"))

def setup(bot):
  bot.add_cog(Memeify(bot))