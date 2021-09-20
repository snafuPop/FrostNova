import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids
import requests
from modules.utils import user_json
from titlecase import titlecase
import sys
import psutil
import time
from datetime import timedelta, datetime

class Info(commands.Cog):
  def __init__(self, bot):
    self.time_alive = time.time()
    self.bot = bot;


  def datetime_to_unix(self, datetime_val):
    # Because many of discord's api requests return time as a datetime object,
    # we need to manually convert it into UNIX time.
    return int(time.mktime((datetime_val).timetuple()))


  def get_uptime(self):
    # Outputs how long the bot has been active.
    uptime = timedelta(seconds = time.time() - self.time_alive)
    uptime = datetime(1,1,1) + uptime
    return "{}d {}h {}m {}s".format(uptime.day-1, uptime.hour, uptime.minute, uptime.second)


  def get_nickname(self, user):
    # Gets the user's nickname within the server.
    # If they have no nickname, a null string is returned.
    if user.nick is not None:
      return "(" + user.nick + ")"
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
    embed = discord.Embed(title = "{}'s avatar".format(str(user)), description = "", color = user.color)
    avatar_url = user.avatar_url if user.avatar_url else user.default_avatar_url
    embed.set_image(url = avatar_url)
    await ctx.send(embed = embed)


  @cog_ext.cog_slash(name = "server", description = "Pulls up information about the current server.")
  async def server(self, ctx):
    server = ctx.guild

    # Constructing the Embed.
    embed = discord.Embed(title = "__**{}**__".format(str(server.name)))
    embed.set_author(name = "Owned by {}".format(server.owner), icon_url = server.owner.avatar_url)

    # Constructing additional information.
    info = []
    info.append("**Location:** {}".format(str(server.region)))
    info.append("**Creation Date:** <t:{}:D>".format(self.datetime_to_unix(server.created_at)))
    info.append("**Members:** {:,}".format(server.member_count))
    info.append("**Boosts:** {:,} Boosts (Level {})".format(server.premium_subscription_count, server.premium_tier))
    if server.description: info.append("*{}*".format(server.description))
    server_info = "\n".join(info)

    # Adding additional fields to the Embed.
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name = "Information:", value = server_info)
    embed.set_footer(text = "Server ID: {}".format(server.id))
    await ctx.send(embed = embed)


  @cog_ext.cog_slash(name = "about", description = "Pulls up information about yvona.")
  async def about(self, ctx):
    # Constructing the Embed.
    embed = discord.Embed(title = "", color = self.bot.user.color)
    embed.set_author(name = "Yvona Bot", url = "https://github.com/snafuPop/yvona", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = self.bot.user.avatar_url)

    # Constructing additional information.
    info = []
    info.append("**Author:** {}".format(await self.bot.fetch_user(94236862280892416)))
    info.append("**Language:** Python {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    info.append("**Discord.py Version:** {}".format(discord.__version__))
    info.append("**Host:** [PythonAnywhere](https://www.pythonanywhere.com/)")
    info.append("**Latency:** {:.4f}ms".format(self.bot.latency))
    info.append("**CPU Usage:** {}%".format(psutil.cpu_percent()))
    info.append("**Disk Usage:** {}%".format(psutil.disk_usage('/')[3]))
    info.append("**Current Uptime:** {}".format(self.get_uptime()))
    info.append("Currently supporting **{:,} servers** and **{:,} users**.".format(len(bot.guilds), len(bot.users)))

    # Adding additional fields to the Embed.
    bot_info = "\n".join(info)
    embed.add_field(name = "**__Bot Statistics__**", value = bot_info)

    # Constructing Buttons.
    buttons = [
      # Invite yvona Button.
      manage_components.create_button(
        style = ButtonStyle.URL,
        label = "Invite yvona",
        url = "https://bit.ly/3kqPgv0"),
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

    # Checks if the user is registered with yvona.
    # If so, additional stats are featured.
    user_dict = user_json.get_users()
    if str(user.id) in user_dict:
      await ctx.send(embed = self.get_registered_user(user, user_dict))
    else:
      await ctx.send(embed = self.get_non_registered_user(user))


  def get_non_registered_user(self, user):
    # Gets statistics of unregistered users.
    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), self.get_nickname(user)), color = user.color)
    embed.set_thumbnail(url = user.avatar_url)

    # Adding additional fields to the Embed.
    info = []
    info.append("**Badges:** {}".format(self.get_flags(user)))
    info.append("**Joined Discord on:** <t:{}:D>".format(self.datetime_to_unix(user.created_at)))
    info.append("**Joined Server on:** <t:{}:D>".format(self.datetime_to_unix(user.joined_at)))

    # Adding additional fields to the Embed.
    user_info = "\n".join(info)
    embed.add_field(name = "Information:", value = user_info)
    embed.set_footer(text = "User ID: {}".format(str(user.id)))
    return embed


  def get_registered_user(self, user, user_dict):
    # Gets statistics of registered users.
    user_key = user_dict[str(user.id)]

    # Constructing the Embed.
    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), self.get_nickname(user)), description = "***Level {:,} {}***".format(user_key["level"], titlecase(str(user.top_role))), color = user.color)
    embed.set_thumbnail(url = user.avatar_url)

    # Constructing additional information.
    info = []
    info.append("**Badges:** {}".format(self.get_flags(user)))
    info.append("**Joined Discord on:** <t:{}:D>".format(self.datetime_to_unix(user.created_at)))
    info.append("**Joined Server on:** <t:{}:D>".format(self.datetime_to_unix(user.joined_at)))

    # Constructing registered user information.
    currency_name = user_json.get_currency_name()
    current_exp = user_key["exp"]
    exp_needed = user_json.get_req_exp(user, user_dict)

    info.append("\n**Text Posts:** {:,}".format(user_key["text_posts"]))
    info.append("**Level:** {:,}/{:,} ({:.2f}%)".format(current_exp, exp_needed, (current_exp/exp_needed)*100))
    info.append("**Current Item Level:** {:,}".format(user_key["item_level"]))
    info.append("**Balance:** {:,} {}".format(user_key["balance"], currency_name))
    info.append("**Embarked Raids:** {:,}".format(user_key["raids"]))
    info.append("**Raid Damage Dealt:** {:,}".format(user_key["damage_dealt"]))
    info.append("**Adventure Wages:** {:,} {}".format(user_key["loot_earnings"], currency_name))
    info.append("**Stolen Wages:** {:,} {}".format(user_key["stolen_money"], currency_name))
    info.append("**Slot Winnings:** {:,} {}".format(user_key["slot_winnings"],  currency_name))

    # Adding additional fields to the Embed.
    user_info = "\n".join(info)
    embed.add_field(name = "Information:", value = user_info, inline = False)
    embed.set_footer(text = "User ID: {}".format(str(user.id)))

    # Adding user's inventory (if it exists) to the Embed.
    items = ", ".join(user_key["inventory"])
    if items:
      embed.add_field(name = "**Inventory:**", value = items)
    embed.set_footer(text = "User ID: {}".format(str(user.id)))
    return embed

def setup(bot):
  bot.add_cog(Info(bot))