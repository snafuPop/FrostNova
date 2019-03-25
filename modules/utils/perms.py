import discord
import discord.utils
from discord.ext import commands

def is_owner_check(ctx):
  # checks if the user if the owner of the bot
  return ctx.message.author.id == '94236862280892416'

def is_owner():
  return commands.check(is_owner_check)