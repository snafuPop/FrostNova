import discord
from discord.ext import commands
from builtins import bot
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


  @commands.command(description = "Prints markdown text utilized by Discord.")
  async def markdown(self, ctx):
    embed = discord.Embed(title = "List of Markdown")
    embed.add_field(name = "Italics", value = "`*italitcs*` or `_italics_`")
    embed.add_field(name = "Bold", value = "`**bold**`")
    embed.add_field(name = "Underline", value = "`__underline__`")
    embed.add_field(name = "Strikethrough", value = "`~~strikethrough~~`")
    embed.add_field(name = "Spoiler", value = "`||spoiler||`")

    embed.add_field(name = "Single-line Code", value = "surround text with `")
    embed.add_field(name = "Multi-line Code", value = "surround text with 3 `'s. Define a language by typing the name of the language after the three backticks")

    await ctx.send(embed = embed)


  @commands.command(pass_context = True, description = "Grabs a user's avatar.")
  async def avatar(self, ctx, *, user: discord.Member = None):
    try:
      if user is None:
        user = ctx.author

    except Exception as e:
      embed = discord.Embed(title = "", description = "It doesn't seem like {} is a member of this server. Maybe try mentioning them instead?".format(str(user)))

    else:
      embed = discord.Embed(title = "{}'s avatar".format(str(user)), description = "", color = user.color)

      if user.avatar_url:
        embed.set_image(url = user.avatar_url)
        if requests.head(user.avatar_url).headers['Content-Type'] == "image/gif":
          embed.set_footer(text = "This user has a .gif avatar because they are a Discord Nitro user. Learn more at https://discordapp.com/nitro")
      else:
        embed.set_image(url = user.default_avatar_url)

    await ctx.send(embed = embed)


  @commands.command(description = "Gives information about a user.")
  async def user(self, ctx, *, user: discord.Member = None):
    # grabbing the user's username (defaults to the author if a user was not specified)
    try:
      if user is None:
        user = ctx.author
    except Exception as e:
      await ctx.send(embed = discord.Embed(title = "", description = "It doesn't seem like {} is a member of this server. Maybe try mentioning them instead?".format(str(user))))
      return
    else:
      # displays register information (if available)
      user_dict = user_json.get_users()
      if str(user.id) in user_dict:
        await ctx.send(embed = self.get_reg_user(user, user_dict))
      else:
        await ctx.send(embed = self.get_non_reg_user(user))

  def get_non_reg_user(self, user):
    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), self.get_nickname(user)), description = "**roles:** {}".format(self.get_roles(user)), color = user.color)
    embed.set_thumbnail(url = user.avatar_url)
    embed.add_field(name = "**Joined Discord on:**", value = str(user.created_at.strftime("%b %d, %Y")))
    embed.add_field(name = "**Joined Server on:**", value = str(user.joined_at.strftime("%b %d, %Y")))
    embed.set_footer(text = "User ID: {}".format(str(user.id)))
    return embed

  def get_reg_user(self, user, user_dict):
    user_key = user_dict[str(user.id)]

    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), self.get_nickname(user)), description = "***Level {:,} {}*** (**{:,}**/{:,} exp)".format(user_key["level"], titlecase(str(user.top_role)), user_key["exp"], user_json.get_req_exp(user, user_dict)), color = user.color)
    embed.set_thumbnail(url = user.avatar_url)
    embed.add_field(name = "**Joined Discord on:**", value = str(user.created_at.strftime("%b %d, %Y")))
    embed.add_field(name = "**Joined Server on:**", value = str(user.joined_at.strftime("%b %d, %Y")))

    currency_name = user_json.get_currency_name()
    stats = []
    stats.append("**Text Posts:** {:,}".format(user_key["text_posts"]))
    stats.append("**Current Item Level:** {:,}".format(user_key["item_level"]))
    stats.append("**Balance:** {:,} {}".format(user_key["balance"], currency_name))
    stats.append("**Embarked Raids:** {:,}".format(user_key["raids"]))
    stats.append("**Raid Damage Dealt:** {:,}".format(user_key["damage_dealt"]))
    stats.append("**Money From Adventures:** {:,} {}".format(user_key["loot_earnings"], currency_name))
    stats.append("**Slot Winnings:** {:,} {}".format(user_key["slot_winnings"], currency_name))
    stats.append("**Pennies Stolen:** {:,} {}".format(user_key["stolen_money"], currency_name))
    embed.add_field(name = "__**Statistics:**__", value = "\n".join(stats), inline = False)

    items = ", ".join(user_key["inventory"])
    if items: embed.add_field(name = "**Inventory:**", value = items)
    embed.set_footer(text = "User ID: {}".format(str(user.id)))
    return embed

  def get_nickname(self, user):
    if user.nick is not None:
      return "(" + user.nick + ")"
    else:
      return ""

  def get_roles(self, user):
    # grabs all of the user's roles (except the default role) and converts it to a string
    roles = []
    for role in user.roles:
      if role.name != "@everyone":
        roles.append(role.name)
    if roles:
      roles = ", ".join(roles)
    else:
      roles = "None"


  @commands.command(aliases = ["guild"], description = "Gives information about the current server.")
  async def server(self, ctx):
    server = ctx.guild

    embed = discord.Embed(title = "__**{}**__".format(str(server.name)), description = "**Owned by:** {}".format(server.owner))
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name = "**Location**:", value = str(server.region))
    embed.add_field(name = "**Creation Date:**", value = server.created_at.strftime("%d %b %Y"))
    embed.add_field(name = "**Members:**", value = "{:,}".format(server.member_count))
    embed.add_field(name = "**Boost:**", value = "{:,} Boosts (Level {})".format(server.premium_subscription_count, server.premium_tier))
    embed.set_footer(text = "Server ID: {}".format(server.id))

    await ctx.send(embed = embed)


  # gives some details about the bot
  @commands.command(aliases = ["bot", "info"], description = "Gives information about the bot")
  async def about(self, ctx):
    embed = discord.Embed(title = " ", color = bot.user.color)
    embed.set_author(name = "Yvona Bot", url = "https://github.com/snafuPop/yvona", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
    embed.set_thumbnail(url = self.bot.user.avatar_url)

    # storing info onto a string to make things a little more readable
    info  = "**\u3164\u25A0 Author:** {}\n".format(await self.bot.fetch_user(94236862280892416))
    info += "**\u3164\u25A0 Language:** Python {}.{}.{}\n".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
    info += "**\u3164\u25A0 Discord.py Version:** {}\n".format(discord.__version__)
    info += "**\u3164\u25A0 Host:** [PythonAnywhere](https://www.pythonanywhere.com/)\n"
    info += "**\u3164\u25A0 Source Code:** [GitHub](https://github.com/snafuPop/yvona)\n"
    info += "**\u3164\u25A0 Latency:** {:.4f} ms\n".format(self.bot.latency)
    info += "**\u3164\u25A0 CPU Usage:** {}%\n".format(psutil.cpu_percent())
    info += "**\u3164\u25A0 Disk Usage:** {}%\n".format(psutil.disk_usage('/')[3])
    info += "**\u3164\u25A0 Current Uptime:** {}\n".format(self.get_uptime())
    info += "**\u3164\u25A0 Servers:** {:,} ({:,} users)\n".format(len(bot.guilds), len(bot.users))
    info += "\n**Submit all bug reports and suggestions to the GitHub:** [Click here](https://github.com/snafuPop/yvona/issues/new)\n"
    info += "Want yvona on _your_ server? [Click here](https://discordapp.com/api/oauth2/authorize?client_id=547516876851380293&permissions=1861483585&scope=bot).\n"
    info += "Like this bot? [Consider donating a dollar or two](https://www.patreon.com/yvona)."

    embed.add_field(name ="**__Bot Statistics__**", value = info)
    embed.set_footer(text = "Use {}help to produce a list of commands".format(ctx.prefix))
    await ctx.send(embed = embed)

  def get_uptime(self):
    uptime = timedelta(seconds = time.time() - self.time_alive)
    uptime = datetime(1,1,1) + uptime
    return "{}d {}h {}m {}s".format(uptime.day-1, uptime.hour, uptime.minute, uptime.second)


def setup(bot):
  bot.add_cog(Info(bot))