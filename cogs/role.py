import discord
from discord import app_commands
from discord.ext import commands

import json
import asyncio
import os

from cogs.utils.keywords import Keyword as ky

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = self.get_roles()


    def get_dirname(self):
        return os.path.dirname(__file__) + "/_data/role.json"


    def get_roles(self):
        with open(self.get_dirname()) as json_data:
            cache = json.load(json_data)
        return cache


    def update_roles(self, cache):
        with open(self.get_dirname(), "w") as json_out:
            json.dump(cache, json_out, indent = 2)
        self.cache = self.get_roles()


    async def can_manage_guild(interaction: discord.Interaction):
        return interaction.user.guild_permissions.manage_guild


    def role_message_exists(self, interaction: discord.Interaction):
        return str(interaction.guild.id) in self.cache


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.guild_id) in self.cache:
            if str(payload.emoji.name) in self.cache[str(payload.guild_id)]["reactions"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][payload.emoji.name])
                user = guild.get_member(payload.user_id)
                await user.add_roles(role)
            else:
                emoji_name = "<:{}:{}>".format(str(payload.emoji.name), str(payload.emoji.id))
                if emoji_name in self.cache[str(payload.guild_id)]["reactions"]:
                    guild = self.bot.get_guild(payload.guild_id)
                    role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][emoji_name])
                    user = guild.get_member(payload.user_id)
                    await user.add_roles(role)



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # listens for reaction removals.
        # if a reaction is removed from a role message for the context's guild, update the context author's roles.
        if str(payload.guild_id) in self.cache:
            if str(payload.emoji.name) in self.cache[str(payload.guild_id)]["reactions"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][payload.emoji.name])
                user = guild.get_member(payload.user_id)
                await user.remove_roles(role)
            else:
                emoji_name = "<:{}:{}>".format(str(payload.emoji.name), str(payload.emoji.id))
                if emoji_name in self.cache[str(payload.guild_id)]["reactions"]:
                    guild = self.bot.get_guild(payload.guild_id)
                    role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][emoji_name])
                    user = guild.get_member(payload.user_id)
                    await user.remove_roles(role)


    role = app_commands.Group(name = "role", description = "Commands that involve creating, modifying, or deleting role-assign messages")
    @role.command(name = "list", description = "Pulls up a list of the server's roles and their IDs")
    @app_commands.guild_only()
    async def get_role_list(self, interaction: discord.Interaction):
        role_list = ""
        for role in interaction.guild.roles:
            if role.name != "@everyone":
                    role_list += f"**{role.name}**: {role.id}\n"
        embed = discord.Embed(title = f"**{interaction.guild.name}'s Roles**", description = role_list)
        await interaction.response.send_message(embed = embed)


    @role.command(name = "create", description = "Creates a new role management message (requires server management permissions)")
    @app_commands.check(can_manage_guild)
    @app_commands.guild_only()
    async def create_role_message(self, interaction: discord.Interaction, title: str, body: str):
        if str(interaction.guild.id) in self.cache:
            embed = discord.Embed(title = "", description = f"{ky.ERROR.value} This server already has a role message. Either delete it with `/role delete`, or modify it using `/role edit`.")
            await interaction.response.send_message(embed = embed)
            return

        cache = self.cache
        embed = discord.Embed(title = title, description = body, color = self.bot.user.color)
        await interaction.response.send_message(embed = embed)
        role_message = await interaction.original_response()
        cache[str(interaction.guild.id)] = {"server_name": interaction.guild.name, "message_id": role_message.id, "reactions": {}}
        self.update_roles(cache)

  
    @role.command(name = "delete", description = "Deletes the server's role management message  (requires server management permissions)")
    @app_commands.check(can_manage_guild)
    @app_commands.guild_only()
    async def delete_role_message(self, interaction: discord.Interaction):
        if not self.role_message_exists(interaction):
            embed = discord.Embed(title = "", description = f"{ky.ERROR.value} This server doesn't have a role message. Also check if this message is in the same channel as the message.")
            await interaction.response.send_message(embed = embed)
            return

        embed = discord.Embed(title = "", description = "Are you sure you want to delete this server's role management message?")
        embed.set_footer(text = "React with 👍 to confirm, or wait 10 seconds to cancel.")
        message = interaction.message
        await interaction.response.send_message(embed = embed)

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) == '👍'

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 10)
        except asyncio.TimeoutError as error:
            embed = discord.Embed(title = "", description = f"**{ky.ERROR.value} {type(error).__name__}:** {error}")
            await interaction.followup.send(embed = embed, ephemeral = True)
        else:
            cache = self.cache
            role_message_id = int(cache[str(interaction.guild.id)]['message_id'])
            to_be_deleted = await interaction.channel.fetch_message(role_message_id)
            await to_be_deleted.delete()

            cache.pop(str(interaction.guild.id))
            self.update_roles(cache)
            embed = discord.Embed(title = "", description = "Successfully deleted this server's role message.")
            await interaction.followup.send(embed = embed)


    @role.command(name = "edit", description = "Edits the server's role management message (requires server management permissions)")
    @app_commands.check(can_manage_guild)
    @app_commands.guild_only()
    async def edit_role_message(self, interaction: discord.Interaction, title: str, body: str):
        if not self.role_message_exists(interaction):
            embed = discord.Embed(title = "", description = f"{ky.ERROR.value} This server doesn't have a role message. Also check if this message is in the same channel as the message.")
            await interaction.response.send_message(embed = embed)
            return

        embed = discord.Embed(title = title, description = body, color = self.bot.user.color)
        role_message_id = int(self.cache[str(interaction.guild.id)]['message_id'])
        to_be_edited = await interaction.channel.fetch_message(role_message_id)
        await to_be_edited.edit(embed = embed)
        embed = discord.Embed(title = "", description = "Successfully edited this server's role message.")


    @role.command(name = "add", description = "Adds an <emoji,role_id> pair to the role management message (requires server management permissions)")
    @app_commands.check(can_manage_guild)
    @app_commands.guild_only()
    async def add_role_reaction_to_message(self, interaction: discord.Interaction, emoji: str, role: discord.Role):
        if not self.role_message_exists(interaction):
            embed = discord.Embed(title = "", description = f"{ky.ERROR.value} This server doesn't have a role message. Also check if this message is in the same channel as the message.")
            await interaction.response.send_message(embed = embed)
            return

        cache = self.cache
        if emoji in list(cache[str(interaction.guild.id)]['reactions']):
            embed = self.bot.create_error_response(message = f"\"{emoji}\" is already being used as a role management reaction.")
            await interaction.response.send_message(embed = embed)
            return

        role_message_id = int(self.cache[str(interaction.guild.id)]['message_id'])
        message = await interaction.channel.fetch_message(role_message_id)

        await message.add_reaction(emoji)
        cache[str(interaction.guild.id)]['reactions'][emoji] = role.id
        self.update_roles(cache)

        embed = discord.Embed(title = "**Successfully added reaction.**", description = f"Reacted with {emoji} to message ID {role_message_id}.")
        embed.set_footer(text = "This message will automatically delete itself after 5 seconds.")

        await interaction.response.send_message(embed = embed)
        await asyncio.sleep(5)
        await interaction.delete_original_response()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))