import discord
from discord.ext import commands
from builtins import bot
import requests
from modules.utils import user_json

class Info(commands.Cog):
  def __init__(self, bot):
    self.bot = bot;
    self.regions = {
      "us-central": ":flag_us: US Central",
      "us-east": ":flag_us: US East",
      "us-south": ":flag_us: US South",
      "us-west": ":flag_us: US West",
      "eu-central": ":flag_eu: Central Europe",
      "eu-west": ":flag_eu: Western Europe",
      "braziL": ":flag_br: Brazil",
      "japan": ":flag_jp: Japan",
      "russia": ":flag_ru: Russia",
      "singapore": ":flag_sg: Singapore",
      "south-africa": ":flag_za: South Africa",
      "sydney": ":flag_au: Sydney"
    }


  @commands.command(description = "Prints markdown text utilized by Discord")
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


  @commands.command(pass_context = True, description = "Grabs a user's avatar")
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


  @commands.command(description = "Gives information about a user")
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
    embed.set_footer(text = "Joined Discord on {}, joined server on {}".format(user.created_at.strftime("%b %d, %Y"), user.joined_at.strftime("%b %d, %Y")))
    return embed

  def get_reg_user(self, user, user_dict):
    user_key = user_dict[str(user.id)]

    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), self.get_nickname(user)), description = "***Level {:,} Adventurer*** (**{:,}**/{:,} exp)".format(user_key["level"], user_key["exp"], user_json.get_req_exp(user, user_dict)), color = user.color)
    embed.set_thumbnail(url = user.avatar_url)
    embed.add_field(name = "**Text Posts:**", value = "{:,} posts".format(user_key["text_posts"]), inline = True)
    embed.add_field(name = "**Balance:**", value = "{:,} {}".format(user_key["balance"], user_json.get_currency_name()), inline = True)

    currency_name = user_json.get_currency_name()
    stats = []
    stats.append("**Successful Raids:** {:,}".format(user_key["raids"]))
    stats.append("**Money From Adventures:** {:,} {}".format(user_key["loot_earnings"], currency_name))
    stats.append("**Slot Winnings:** {:,} {}".format(user_key["slot_winnings"], currency_name))
    stats.append("**Pennies Stolen:** {:,} {}".format(user_key["stolen_money"], currency_name))
    embed.add_field(name = "\u3164", value = "\n".join(stats), inline = False)
    embed.set_footer(text = "Joined Discord on {}, joined server on {}".format(user.created_at.strftime("%b %d, %Y"), user.joined_at.strftime("%b %d, %Y")))
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

  @commands.command(description = "Gives information about the current server")
  async def server(self, ctx):
    server = ctx.guild
    embed = discord.Embed(title = "__**{}**__ ({})".format(str(server.name), self.regions[str(server.region)]), description = "<{}>".format(server.id))
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name = "Number of members:", value = str(server.member_count), inline = True)
    embed.add_field(name = "Owner", value = str(server.owner), inline = True)
    embed.set_footer(text = "Server was founded on {}".format(server.created_at.strftime("%d %b %Y")))

    await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Info(bot))