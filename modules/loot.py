import discord
from discord.ext import commands
from builtins import bot
import random
import math
from modules.utils import user_json

class Loot(commands.Cog):
  def __init__(bot):
    self.bot = bot

  @commands.is_owner()
  @commands.command(hidden = True, description = "Adds an item to the snafuStore")
  async def add_item(self, ctx, *args):
    if args is None or len(args) != 2:
      await ctx.send(embed = discord.Embed(title = "", description = "Invalid args"))
      return


  @commands.command(aliases = ["store"], description = "DM's the snafuStore's inventory")
  async def shop(self, ctx):
    pass