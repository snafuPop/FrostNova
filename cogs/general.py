import discord
from discord import app_commands
from discord.ext import commands

import os
import json
import time
from datetime import timedelta, datetime
import boto3
from botocore.config import Config
import sys
import psutil

from cogs.utils.keywords import Keyword as ky


class General(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.time_alive = time.time()

  def convert_datetime_to_unix(self, datetime_val):
    # because many of discord's api requests return time as a datetime object,
    # we need to manually convert it into the UNIX time format
    return int(time.mktime((datetime_val).timetuple()))


  def get_uptime(self):
    uptime = timedelta(seconds = time.time() - self.time_alive)
    uptime = datetime(1,1,1) + uptime
    return f"{uptime.day-1}d {uptime.hour}h {uptime.minute}m {uptime.second}s"


  @app_commands.command(name = "wave", description = "Say hi!")
  async def wave(self, interaction: discord.Interaction):
    embed = discord.Embed(title = "", description = f"Hi, {interaction.user.mention}! :wave:")
    embed.set_footer(text = f"{round(self.bot.latency*1000)}ms response time")
    await interaction.response.send_message(embed = embed)


  @app_commands.command(name = "about", description = "Pulls up information about FrostNova.")
  async def about(self, interaction: discord.Interaction):
    embed = discord.Embed(title = "", color = self.bot.user.color)
    embed.set_author(name = self.bot.user.name, url = "https://github.com/snafuPop/FrostNova", icon_url = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    embed.set_thumbnail(url = self.bot.user.avatar.url)

    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()['Reservations'][0]['Instances'][0]

    statistics = "\n".join([
      f"{ky.BULLET.value} **Author:** {await self.bot.fetch_user(94236862280892416)}",
      f"{ky.BULLET.value} **Language:** Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
      f"{ky.BULLET.value} **Discord.py:** v{discord.__version__}",
      f"{ky.BULLET.value} **Host:** aws ec2 {response['InstanceType']} instance",
      f"{ky.BULLET.value} **Platform:** {response['Architecture']} {response['PlatformDetails']}",
      f"{ky.BULLET.value} **Latency:** {self.bot.latency:.4f}ms",
      f"{ky.BULLET.value} **CPU Usage:** {psutil.cpu_percent()}",
      f"{ky.BULLET.value} **Memory Usage:** {psutil.virtual_memory()[2]}%",
      f"{ky.BULLET.value} **Disk Usage:** {psutil.disk_usage('/')[3]}%",
      f"{ky.BULLET.value} **Current Uptime:** {self.get_uptime()}",
      f"Currently supporting **{len(self.bot.guilds):,}** guilds."])
    embed.add_field(name = "**Statistics**", value = statistics)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = "Invite", style = discord.ButtonStyle.link, url = "https://discord.com/api/oauth2/authorize?client_id=547516876851380293&permissions=8&scope=bot"))
    view.add_item(discord.ui.Button(label = "Repo", style = discord.ButtonStyle.link, url = "https://github.com/snafuPop/FrostNova"))
    view.add_item(discord.ui.Button(label = "Report an Issue", style = discord.ButtonStyle.link, url = "https://github.com/snafuPop/FrostNova/issues/new"))

    await interaction.response.send_message(embed = embed, view = view)


  @app_commands.command(name = "server", description = "Pulls up information about the current server.")
  @app_commands.guild_only()
  async def server(self, interaction: discord.Interaction):
    guild = interaction.guild
    guild_desc = f"*{guild.description}*" if guild.description else ""
    embed = discord.Embed(title = f"**{guild.name}**", description = guild_desc)
    embed.set_author(name = f"Owned by {guild.owner}", icon_url = guild.owner.avatar.url)

    statistics = "\n".join([
      f"{ky.BULLET.value} **Founded on:** <t:{self.convert_datetime_to_unix(guild.created_at)}:D>",
      f"{ky.BULLET.value} **Members:** {guild.member_count:,}",
      f"{ky.BOOST.value} **Boosts:** {guild.premium_subscription_count:,} (Lv. {guild.premium_tier})"])

    def get_symbol(feature):
      return ky.SUCCESS.value if feature in guild.features else ky.NO.value

    features = "\n".join([
      f"{get_symbol('COMMUNITY')} Community Server",
      f"{get_symbol('PARTNERED')} Partnered",
      f"{get_symbol('VERIFIED')} Partnered",
      f"{get_symbol('DISCOVERABLE')} Featured on Server Discovery",
      f"{get_symbol('MEMBER_VERIFICATION_GATE_ENABLED')} Membership Screening enabled",
      f"{get_symbol('MONETIZATION_ENABLED')} Monetization enabled"])

    embed.set_thumbnail(url = guild.icon.url)
    embed.add_field(name = "**Statistics:**", value = statistics + "\n\n" + features)
    embed.set_footer(text = f"Server ID: {guild.id}")
    await interaction.response.send_message(embed = embed)


  @app_commands.command(name = "avatar", description = "Pulls up a user's profile picture.")
  @app_commands.guild_only()
  @app_commands.describe(user = "The user who's profile picture you'd like to see. Leave blank to pull up your own.")
  async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
    if not user:
      user = interaction.user
    embed = discord.Embed(title = f"{user.display_name}'s Profile Picture", description = "", color = user.color)
    avatar = user.display_avatar if user.display_avatar else user.default_avatar
    embed.set_image(url = avatar.url)
    await interaction.response.send_message(embed = embed)


  @app_commands.command(name = "user", description = "Pulls up information about a user")
  @app_commands.guild_only()
  @app_commands.describe(user = "The user who you want to pull up information on. Leave blank to pull up your own.")
  async def user(self, interaction: discord.Interaction, user: discord.Member = None):
    if not user:
      user = interaction.user

    name_string = f"**{user.name}**" if not user.nick else f"**{user.name}**, a.k.a. *{user.display_name}*"
    if user.bot:
      name_string += " :robot:"
    embed = discord.Embed(title = name_string, color = user.color)
    embed.set_thumbnail(url = user.display_avatar.url)

    flags = []
    for flag in user.public_flags.all():
      flag_name = flag.name
      flag_name = flag_name.replace("_", " ").title()
      flags.append(flag_name)
    flag_list = ", ".join(flags) if flags else None

    statistics = "\n".join([
      f"{ky.BULLET.value} **Badges:** {flag_list}",
      f"{ky.BULLET.value} **Joined Discord on:** <t:{self.convert_datetime_to_unix(user.created_at)}:D>",
      f"{ky.BULLET.value} **Joined {interaction.guild} on:** <t:{self.convert_datetime_to_unix(user.joined_at)}:D>"])

    embed.add_field(name = "**Statistics:**", value = statistics)
    embed.set_footer(text = f"User ID:{user.id}")
    await interaction.response.send_message(embed = embed)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(General(bot))