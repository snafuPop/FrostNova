import discord
from discord.ext import commands
from builtins import bot
import json

class Roles(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.cache = self.get_roles()

  def get_roles(self):
    with open("/home/snafuPop/yshtola/modules/_data/role.json") as json_data:
      cache = json.load(json_data)
    return cache

  def update_roles(self, cache):
    with open("/home/snafuPop/yshtola/modules/_data/role.json", "w") as json_out:
      json.dump(cache, json_out, indent = 2)
    self.cache = self.get_roles()


  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    if str(payload.guild_id) in self.cache:
      if str(payload.emoji.name) in self.cache[str(payload.guild_id)]["reactions"]:
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][payload.emoji.name])
        user = guild.get_member(payload.user_id)
        await user.add_roles(role)
        # for discord 1.3
        #if payload.event_type is "REACTION_ADD":
        #  await user.add_roles(role)
        #if payload.event_type is "REACTION_REMOVE":
        #  await user.remove_roles(role)

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload):
    if str(payload.guild_id) in self.cache:
      if str(payload.emoji.name) in self.cache[str(payload.guild_id)]["reactions"]:
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(self.cache[str(payload.guild_id)]["reactions"][payload.emoji.name])
        user = guild.get_member(payload.user_id)
        await user.remove_roles(role)

  @commands.command(description = "Gets a list of a server's roles and their IDs.")
  async def server_roles(self, ctx):
    role_list = ""
    for role in ctx.guild.roles:
      if role.name is not "@everyone":
        role_list = role_list + "**{}**: ".format(role.name) + str(role.id) + "\n"
    await ctx.send(embed = discord.Embed(title = "**{}'s Roles**".format(ctx.guild.name), description = role_list))

  @commands.command(description = "Add a role message to be stored. Role messages allow you to let members assign their own roles using reactions.")
  async def role_msg(self, ctx, *, message: str = "Use the reactions below to assign yourself a role!"):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to create a role message."))
      return

    if str(ctx.guild.id) in self.cache:
      await ctx.send(embed = discord.Embed(title = "**This server already has a role message.**", description = "Delete the original role message first using `{}delete_role_msg`.".format(ctx.prefix)))
      return

    cache = self.cache
    role_msg = await ctx.send(embed = discord.Embed(title = "", description = message, color = ctx.author.color))
    cache[str(ctx.guild.id)] = {"server_name": ctx.guild.name, "message_id": role_msg.id, "reactions": {}}
    self.update_roles(cache)


  @commands.command(description = "Deletes the server's role message.")
  async def delete_role_msg(self, ctx):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to delete a role message."))
      return
    if str(ctx.guild.id) not in self.cache:
      await ctx.send(embed = discord.Embed(title = "**Error**", description = "This server does not have a role message. You can create one using `{}role_msg`.".format(ctx.prefix)))
      return

    cache = self.cache
    to_be_deleted = await ctx.fetch_message(int(cache[str(ctx.guild.id)]["message_id"]))
    await to_be_deleted.delete()
    cache.pop(str(ctx.guild.id))
    self.update_roles(cache)
    await ctx.send(embed = discord.Embed(title = "", description = "Successfully deleted this server's role message."))


  @commands.command(description = "Edits the server's role message.s")
  async def edit_role_msg(self, ctx, *, message: str = "Use the reactions below to assign yourself a role!"):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to create a role message."))
      return
    if str(ctx.guild.id) not in self.cache:
      await ctx.send(embed = discord.Embed(title = "**Error**", description = "This server does not have a role message. You can create one using `{}role_msg`.".format(ctx.prefix)))
      return

    role_msg = discord.Embed(title = "", description = message, color = ctx.author.color)
    to_be_edited = await ctx.fetch_message(int(self.cache[str(ctx.guild.id)]["message_id"]))
    await to_be_edited.edit(embed = role_msg)


  @commands.command(description = "Adds a role reaction to the server's role message.")
  async def add_role_reaction(self, ctx, emoji: str = None, role_id: int = -1):
    if not ctx.author.guild_permissions.manage_guild:
      await ctx.send(embed = discord.Embed(title = "**You don't have permission to do this.**", description = "You need to be able to change server settings in order to modify a role message."))
      return
    if str(ctx.guild.id) not in self.cache:
      await ctx.send(embed = discord.Embed(title = "**Error**", description = "This server does not have a role message. You can create one using `{}role_msg`.".format(ctx.prefix)))
      return
    if emoji is None or role_id == -1:
      await ctx.send(embed = discord.Embed(title = "", description = "You can add a reaction to this server's role message using `{}add_role_reaction <emoji> <role_id>`.".format(ctx.prefix)))
      return

    msg = await ctx.fetch_message(self.cache[str(ctx.guild.id)]["message_id"])
    try:
      await msg.add_reaction(str(emoji))
    except:
      await ctx.send(embed = discord.Embed(title = "**Error!**", description = "`{}` is not a valid emoji.".format(emoji)))
    cache = self.cache
    cache[str(ctx.guild.id)]["reactions"][str(emoji)] = int(role_id)
    self.update_roles(cache)




def setup(bot):
  bot.add_cog(Roles(bot))