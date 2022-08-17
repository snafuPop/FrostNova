import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from typing import Literal
import os
import json
import asyncio

from cogs.utils.keywords import Keyword as ky


class Maint(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  async def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 94236862280892416


  @app_commands.check(is_owner)
  @app_commands.command(name = "sync", description = "Forces the list of commands to synchronize.")
  async def sync(self, interaction: discord.Interaction, option: Literal["to global", "to guild", "from global", "clear from guild", "global clear"]):
    await interaction.response.defer()
    synced_commands = []
    match option:
      case "to global":
        synced_commands = await self.bot.tree.sync()
      case "to guild":
        synced_commands = await self.bot.tree.sync(guild = interaction.guild)
      case "from global":
        self.bot.tree.copy_global_to(guild = interaction.guild)
        synced_commands = await self.bot.tree.sync(guild = interaction.guild)
      case "clear from guild":
        self.bot.tree.clear_commands(guild = interaction.guild)
        await self.bot.tree.sync(guild = interaction.guild)
      case "global clear":
        self.bot.tree.clear_commands(guild = None)
        await self.bot.tree.sync()

    await interaction.followup.send(embed = discord.Embed(title = "", description = f"Synced {len(synced_commands)} commands."))


  @app_commands.check(is_owner)
  @app_commands.command(name = "shutdown", description = "Terminates the bot.")
  async def shutdown(self, interaction: discord.Interaction):
    embed = discord.Embed(title = "", description = "Are you sure you want to shut me down? （＞人＜；）")
    embed.set_footer(text = "React with 👍 to confirm, or wait 10 seconds to cancel.")
    message = interaction.message
    await interaction.response.send_message(embed = embed)

    def check(reaction, user):
      return user == interaction.user and str(reaction.emoji) == '👍'

    try:
      reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 10)
    except asyncio.TimeoutError as error:
      embed = self.bot.create_error_response(error = error)
      await interaction.followup.send(embed = embed, ephemeral = True)
    else:
      embed = discord.Embed(title = "", description = "Shutting down. Goodbye! :wave:")
      await interaction.followup.send(embed = embed)
      print("\nTerminated via the /shutdown command.")
      await self.bot.close()



  @app_commands.check(is_owner)
  @app_commands.command(name = "load", description = "Loads an unloaded cog.")
  @app_commands.choices(cog = [Choice(name = str(cog_name), value = value) for (value, cog_name) in enumerate(os.listdir("cogs"), 1) if cog_name.endswith(".py") and cog_name != "maint.py"])
  async def load(self, interaction: discord.Interaction, cog: Choice[int]):
    try:
      await self.bot.load_extension("cogs." + cog.name[:-3])
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
      embed = discord.Embed(title = "", description = f"**{ky.ERROR.value} {type(error).__name__}:** {error}")
    else:
      embed = discord.Embed(title = "", description = f"{ky.LOAD.value} `{cog.name}` was loaded.")
    await interaction.response.send_message(embed = embed)


  @app_commands.check(is_owner)
  @app_commands.command(name = "unload", description = "Unloads a loaded cog.")
  @app_commands.choices(cog = [Choice(name = str(cog_name), value = value) for (value, cog_name) in enumerate(os.listdir("cogs"), 1) if cog_name.endswith(".py") and cog_name != "maint.py"])
  async def unload(self, interaction: discord.Interaction, cog: Choice[int]):
    try:
      await self.bot.unload_extension("cogs." + cog.name[:-3])
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
    else:
      embed = discord.Embed(title = "", description = f"{ky.UNLOAD.value} `{cog.name}` was unloaded.")
    await interaction.response.send_message(embed = embed)

  
  @app_commands.check(is_owner)
  @app_commands.command(name = "reload", description = "Reloads a loaded cog.")
  @app_commands.choices(cog = [Choice(name = str(cog_name), value = value) for (value, cog_name) in enumerate(os.listdir("cogs"), 1) if cog_name.endswith(".py")])
  async def reload(self, interaction: discord.Interaction, cog: Choice[int]):
    try:
      await self.bot.reload_extension("cogs." + cog.name[:-3])
    except Exception as error:
      embed = self.bot.create_error_response(error = error)
    else:
      embed = discord.Embed(title = "", description = f"{ky.RELOAD.value} `{cog.name}` was reloaded.")
    await interaction.response.send_message(embed = embed)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Maint(bot))