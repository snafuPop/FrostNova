import discord
from discord.ext import commands
from discord.utils import get
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import emoji_to_dict
from builtins import bot, guild_ids
import json
import asyncio
import os

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



  async def has_permissions(self, ctx):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to create a role message."))
      return False
    else:
      return True



  async def role_msg_exists(self, ctx):
    if str(ctx.guild.id) not in self.cache:
      await ctx.send(embed = discord.Embed(title = "**This server does not have a role message.**", description = "You must create a role message first before modifying it. Make sure you're also issuing commands in the same channel that contains the role message."))
      return False
    else:
      return True



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



  @cog_ext.cog_subcommand(base = "role", name = "list", description = "Returns a list of the current server's roles and their IDs.")
  async def roles(self, ctx):
    role_list = ""
    for role in ctx.guild.roles:
      if role.name != "@everyone":
        role_list = role_list + "**{}**: ".format(role.name) + str(role.id) + "\n"
    await ctx.send(embed = discord.Embed(title = "**{}'s Roles**".format(ctx.guild.name), description = role_list))



  @cog_ext.cog_subcommand(base = "role", name = "create", description = "⛔ Creates a new message on the server to listen for role-updates. You must have management rights.", 
  		options = [create_option(
  			name = "message",
  			description = "The body of the role reaction message.",
  			option_type = 3,
  			required = True),
  		create_option(
  			name = "title",
  			description = "Title of the message.",
  			option_type = 3,
  			required = False)])
  async def create_role_msg(self, ctx, title: str = "", message: str = None):
    if not await self.has_permissions(ctx):
      return

    if str(ctx.guild.id) in self.cache:
      await ctx.send(embed = discord.Embed(title = "**This server already has a role message.**", description = "Either delete the original role message or edit it instead."))
      return

    cache = self.cache
    role_msg = await ctx.send(embed = discord.Embed(title = "{}".format(title), description = message, color = ctx.author.color))
    cache[str(ctx.guild.id)] = {"server_name": ctx.guild.name, "message_id": role_msg.id, "reactions": {}}
    self.update_roles(cache)



  @cog_ext.cog_subcommand(base = "role", name = "delete", description = "⛔ Deletes the role message on the server. You must have management rights.")
  async def delete_role_msg(self, ctx):
    if (not await self.has_permissions(ctx)) or (not await self.role_msg_exists(ctx)):
      return

    cache = self.cache
    try:
      to_be_deleted = await ctx.fetch_message(int(cache[str(ctx.guild.id)]["message_id"]))
      await to_be_deleted.delete()
    except:
      print("Message was already deleted?", flush = True)
    cache.pop(str(ctx.guild.id))
    self.update_roles(cache)
    await ctx.send(embed = discord.Embed(title = "", description = "Successfully deleted this server's role message."))



  @cog_ext.cog_subcommand(base = "role", name = "edit", description = "⛔ Edits the role message on the server. You must have management rights.", 
		options = [create_option(
  			name = "message",
  			description = "The body of the role reaction message.",
  			option_type = 3,
  			required = True),
  		create_option(
  			name = "title",
  			description = "Title of the message.",
  			option_type = 3,
  			required = False)])
  async def edit_role_msg(self, ctx, title: str = "", message: str = None):
    if (not await self.has_permissions(ctx)) or (not await self.role_msg_exists(ctx)):
      return

    role_msg = discord.Embed(title = "", description = message, color = ctx.author.color)
    to_be_edited = await ctx.fetch_message(int(self.cache[str(ctx.guild.id)]["message_id"]))
    await to_be_edited.edit(embed = role_msg)



  @cog_ext.cog_subcommand(base = "role", name = "add", description = "⛔ Adds a <emoji, role_id> pair to the role reaction message. You must have management rights.",
  	options = [create_option(
  		name = "emoji",
  		description = "The emoji reaction to be added.",
  		option_type = 3,
      required = True),
    create_option(
      name = "role",
      description = "The role to be associated with the emoji.",
      option_type = 8,
      required = True)])
  async def add_role_reaction(self, ctx, emoji: str = None, role: discord.Role = None):
    if (not await self.has_permissions(ctx)) or (not await self.role_msg_exists(ctx)):
      return

    msg = await ctx.channel.fetch_message(self.cache[str(ctx.guild.id)]["message_id"])
    emoji_name = emoji_to_dict(emoji)["name"]

    try:
      print(emoji_name)
      await msg.add_reaction(emoji_name)
      cache = self.cache
      cache[str(ctx.guild.id)]["reactions"][emoji_name] = role.id
      self.update_roles(cache)

      embed = discord.Embed(title = "**Successfully added reaction.**", description = "Reacted with {} to message ID {}.".format(emoji_name, msg.id))
      embed.set_footer(text = "This message will automatically delete itself in 3 seconds.")
      sent = await ctx.send(embed = embed)
      print(type(sent))
      await asyncio.sleep(3)
      await sent.delete()

    except Exception as error:
      await ctx.send(embed = discord.Embed(title = "**{}**".format(type(error).__name__), description = error))




def setup(bot):
  bot.add_cog(Roles(bot))