import discord
import discord.utils
from discord.ext import commands

async def is_owner(ctx):
  return ctx.author.id == 316026178463072268