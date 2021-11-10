import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from ButtonPaginator import Paginator
from builtins import bot, guild_ids

import requests
from modules.utils import user_json
from titlecase import titlecase
import sys
import psutil
import time
from datetime import timedelta, datetime

import boto3
from botocore.config import Config

my_config = Config(
  region_name = "us-east-1a")

class Info(commands.Cog):
  def __init__(self, bot):
    self.time_alive = time.time()
    self.bot = bot
    self.bullet_dict = {
      "basic": "▪️",
      "money": user_json.get_currency_name(),
      "boost": "<:boost:907765841771257928>"
    }


  def get_bullet(self, key):
    return self.bullet_dict[key]


  def datetime_to_unix(self, datetime_val): 
    # Because many of discord's api requests return time as a datetime object,
    # we need to manually convert it into UNIX time.
    return int(time.mktime((datetime_val).timetuple()))


  def get_uptime(self):
    # Outputs how long the bot has been active.
    uptime = timedelta(seconds = time.time() - self.time_alive)
    uptime = datetime(1,1,1) + uptime
    return f"{uptime.day-1}d {uptime.hour}h {uptime.minute}m {uptime.second}s"


  def get_nickname(self, user):
    # Gets the user's nickname within the server.
    # If they have no nickname, a null string is returned.
    if user.nick is not None:
      return f"({user.nick})"
    else:
      return ""


  def get_flags(self, user):
    # Gets all of the public flags attributed to the user.
    # If user has no public flags, string "None" is returned.
    flags = []
    user_flags = user.public_flags.all()
    if not user_flags:
      return "None"
    else:
      for flag in user.public_flags.all():
        flags.append(titlecase(str(flag).replace("UserFlags.", "").replace("_", " ")))
      return ", ".join(flags) 


  @cog_ext.cog_slash(name = "avatar", description = "Pulls up a user's profile picture.", 
    options = [create_option(
      name = "user",
      description = "The name of a user. Leave blank to pull up your own profile picture.",
      option_type = 6,
      required = False)])
  async def avatar(self, ctx, user: discord.Member = None):
    # If no user is specified, the author is set as the user.
    if user is None:
      user = ctx.author

    # Constructing the Embed.
    embed = discord.Embed(title = f"{str(user)}'s avatar", description = "", color = user.color)
    avatar_url = user.avatar_url if user.avatar_url else user.default_avatar_url
    embed.set_image(url = avatar_url)
    await ctx.send(embed = embed)


  @cog_ext.cog_slash(name = "server", description = "Pulls up information about the current server.")
  async def server(self, ctx):
    server = ctx.guild

    # Constructing the Embed.
    server_description = f"*{server.description}*" if server.description != None else ""
    embed = discord.Embed(title = f"**{str(server.name)}**", description = server_description)
    embed.set_author(name = f"Owned by {server.owner}", icon_url = server.owner.avatar_url)

    # Constructing additional information.
    bullet = self.get_bullet("basic")
    server_info = "\n".join([
      f"{bullet} **Location:** {str(server.region)}",
      f"{bullet} **Creation Date:** <t:{self.datetime_to_unix(server.created_at)}:D>",
      f"{bullet} **Members:** {server.member_count}",
      f"{self.get_bullet('boost')} **Boosts:** {server.premium_subscription_count:,} (Lv. {server.premium_tier})"
    ])

    # Adding additional fields to the Embed.
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name = "Information:", value = server_info)
    embed.set_footer(text = f"Server ID: {server.id}")
    await ctx.send(embed = embed)


  def get_ec2_info(self):
    # returns information about the current ec2 instance
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()['Reservations'][0]['Instances'][0]
    return response


  @cog_ext.cog_slash(name = "about", description = "Pulls up information about yvona.")
  async def about(self, ctx):
    # Constructing the Embed.
    embed = discord.Embed(title = "", color = self.bot.user.color)
    embed.set_author(name = "Yvona Bot", url = "https://github.com/snafuPop/yvona", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = self.bot.user.avatar_url)
    response = self.get_ec2_info()
    
    # Constructing additional information.
    bullet = self.get_bullet("basic")
    bot_info = "\n".join([
      f"{bullet} **Author:** {await self.bot.fetch_user(94236862280892416)}",
      f"{bullet} **Language:** Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
      f"{bullet} **Discord.py Version:** {discord.__version__}",
      f"{bullet} **Host:** aws ec2 {response['InstanceType']} instance",
      f"{bullet} **Platform:** {response['Architecture']} {response['PlatformDetails']}",
      f"{bullet} **Latency:** {self.bot.latency:.4f}ms",
      f"{bullet} **CPU Usage:** {psutil.cpu_percent()}\%",
      f"{bullet} **Memory Usage:** {psutil.virtual_memory()[2]}\%",
      f"{bullet} **Disk Usage:** {psutil.disk_usage('/')[3]}\%",
      f"{bullet} **Current Uptime:** {self.get_uptime()}",
      f"Currently supporting **{len(bot.guilds):,}** and **{len(bot.users):,}** users."
    ])

    embed.add_field(name = "**Bot Statistics**", value = bot_info)

    # Constructing Buttons.
    buttons = [
      # Invite yvona Button.
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "Invite yvona",
        url = "https://bit.ly/3hStVZH"),
      # Github repo Button.
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "GitHub repo",
        url = "https://github.com/snafuPop/yvona"),
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "Report an issue",
        url = "https://github.com/snafuPop/yvona/issues/new")]
    action_row = manage_components.create_actionrow(*buttons)
    await ctx.send(embed = embed, components = [action_row])


  @cog_ext.cog_slash(name = "user", description = "Pulls up information about a user.",
    options = [create_option(
      name = "user",
      description = "The name of a user. Leave blank to pull up your own information.",
      option_type = 6,
      required = False)])
  async def user(self, ctx, user: discord.Member = None):
    # If no user is specified, the author is set as the user.
    if user is None:
      user = ctx.author

    embeds = []
    embeds.append(self.get_non_registered_user_info(ctx)) # Page 1 consists of general information provided by Discord

    user_dict = user_json.get_users()
    if str(user.id) in user_dict:
      embeds.append(self.get_registered_user_info(user, user_dict)) # Page 2 consists of yvona-specific information, if the user is registered.
      paginated_embed = Paginator(bot = self.bot, ctx = ctx, embeds = embeds, only = ctx.author)
      await paginated_embed.start()
    else:
      await ctx.send(embed = embeds[0])


  def get_non_registered_user_info(self, ctx):
    user = ctx.author

    # Gets statistics of unregistered users.
    embed = discord.Embed(title = f"**{str(user)}** {self.get_nickname(user)}", color = user.color)
    embed.set_thumbnail(url = user.avatar_url)

    # Adding additional fields to the Embed.
    bullet = self.get_bullet("basic")
    user_info = "\n".join([
      f"{bullet} **Badges:** {self.get_flags(user)}",
      f"{bullet} **Joined Discord:** <t:{self.datetime_to_unix(user.created_at)}:D>",
      f"{bullet} **Joined {ctx.guild.name} on:** <t:{self.datetime_to_unix(user.joined_at)}:D>"
    ])

    # Adding additional fields to the Embed.
    embed.add_field(name = "Discord Stats:", value = user_info)
    embed.set_footer(text = f"User ID: {str(user.id)}")
    return embed


  def get_registered_user_info(self, user, user_dict):
    # Gets statistics of registered users.
    user_key = user_dict[str(user.id)]

    # Constructing the Embed.
    embed = discord.Embed(title = f"**{str(user)}** {self.get_nickname(user)}", color = user.color)
    embed.set_thumbnail(url = user.avatar_url)

    # Constructing registered user information.
    currency_name = user_json.get_currency_name()
    current_exp = user_key["exp"]
    exp_needed = user_json.get_req_exp(user, user_dict)

    # Adding additional fields to the Embed.
    bullet = self.get_bullet("basic")
    money = self.get_bullet("money")
    user_info = "\n".join([
      f"{bullet} **Text Posts:** {user_key['text_posts']:,}",
      f"{bullet} **Level:** {user_key['level']:,}",
      f"{bullet} **EXP:** {current_exp:,}/{exp_needed:,} ({current_exp/exp_needed*100:.2f}\%)",
      f"{money} **Balance:** {user_key['balance']:,}",
      f"{money} **Adventure Wages:** {user_key['loot_earnings']:,}",
      f"{money} **Stolen Wages:** {user_key['stolen_money']:,}",
      f"{money} **Slot Winnings:** {user_key['slot_winnings']:,}"
    ])

    # Adding additional fields to the Embed.
    embed.add_field(name = "yvona Stats:", value = user_info, inline = False)

    # Adding user's inventory (if it exists) to the Embed.
    items = ", ".join(user_key["inventory"])
    if items:
      embed.add_field(name = "**Inventory:**", value = items)
    embed.set_footer(text = f"User ID: {str(user.id)}")
    return embed


def setup(bot):
  bot.add_cog(Info(bot))