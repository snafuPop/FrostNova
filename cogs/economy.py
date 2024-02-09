import discord
from discord import app_commands
from discord.ext import commands
from cogs.utils.keywords import Keyword as ky
import cogs.utils.user_utils as user_utils


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    async def is_owner(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 94236862280892416

    
    def is_not_registered_message(self, user):
        '''Returns an embed message intended for interactions that cannot be performed because the designated user is not registered.'''
        return self.bot.create_error_response(message=f"{user.name} is not registered!")
    
    
    def set_balance(self, user, balance):
        '''Sets a user's balance to the specified amount. This function assumes that the user is properly registered in the dictionary of
        registered users. Attempting to set the user's balance to a negative number will set it to 0 instead.'''
        if balance < 0:
            balance = 0
        user_dict = user_utils.get_users()
        user_dict[str(user.id)]["balance"] = balance
        user_utils.update(user_dict)

    
    balance = app_commands.Group(name = "balance", description = "Modifies a user's balance.")

    @app_commands.check(is_owner)
    @balance.command(name = "set", description = "Sets a user's balance to a specified amount")
    @app_commands.describe(user="The target user", balance="The amount to set the user's balance to")
    async def set_balance_to(self, interaction: discord.Interaction, user: discord.Member, balance: int):
        if not user_utils.is_registered(user):
            await interaction.response.send_message(embed=self.is_not_registered_message(user), ephemeral=True)
            return
        self.set_balance(user, balance)
        embed = discord.Embed(title="", description=f"{ky.SUCCESS.value} Successfully set {user.name}'s balance to {balance:,} {ky.CURRENCY.value}.")
        await interaction.response.send_message(embed=embed)
        
        
    @app_commands.check(is_owner)
    @balance.command(name = "add", description = "Adds a specified amount to a user's balance")
    @app_commands.describe(user="The target user", balance="The amount to add onto the user's balance")
    async def add_balance(self, interaction: discord.Interaction, user: discord.Member, balance: int):
        if not user_utils.is_registered(user):
            await interaction.response.send_message(embed=self.is_not_registered_message(user), ephemeral=True)
            return
        self.set_balance(user, user_utils.get_balance(user) + balance)
        embed = discord.Embed(title="", description=f"{ky.SUCCESS.value} Successfully added {balance:,} {ky.CURRENCY.value} to {user.name}'s balance.")
        await interaction.response.send_message(embed=embed)
        
        
    @app_commands.check(is_owner)
    @balance.command(name = "subtract", description = "Subtracts a specified amount to a user's balance")
    @app_commands.describe(user="The target user", balance="The amount to subtract from the user's balance")
    async def subtract_balance(self, interaction: discord.Interaction, user: discord.Member, balance: int):
        if not user_utils.is_registered(user):
            await interaction.response.send_message(embed=self.is_not_registered_message(user), ephemeral=True)
            return
        self.set_balance(user, user_utils.get_balance(user) - balance)
        embed = discord.Embed(title="", description=f"{ky.SUCCESS.value} Successfully removed {balance:,} {ky.CURRENCY.value} from {user.name}'s balance.")
        await interaction.response.send_message(embed=embed)
        

    @app_commands.command(name="register", description="Registers yourself on the payroll registrar.")
    async def register(self, interaction: discord.Interaction):
        if user_utils.is_registered(interaction.user):  # check if the user is already registered
            embed = discord.Embed(
                title = "",
                description = "It seems you're already listed in the registrar—confirm by checking if your balance is available when invoking `/user` on yourself."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_dict = user_utils.get_users()
        user_dict[str(interaction.user.id)] = user_utils.get_default_keys()
        user_utils.update(user_dict)
        embed = discord.Embed(
            title = "You have been successfully registered!",
            description = f"I've also given you complimentary sum of {user_utils.get_balance(interaction.user):,} {ky.CURRENCY.value}. Have fun!"
        )
        await interaction.response.send_message(embed=embed)
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Economy(bot))