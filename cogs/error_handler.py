import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import AppCommandError
import sys
import traceback

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error


    async def on_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = self.bot.create_error_response(message=str(error))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif isinstance(error, app_commands.CheckFailure):
            message = "You do not have the required permission(s) to run this command."
            embed = self.bot.create_error_response(message = message)
            await interaction.response.send_message(embed = embed, ephemeral=True)

        else:
            print(f"Ignoring exception in command {interaction}:")
            traceback.print_exception(type(error), error, error.__traceback__)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommandErrorHandler(bot))