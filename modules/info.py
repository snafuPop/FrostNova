import discord
from discord.ext import commands
from builtins import bot
import requests
import json

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

  @commands.command(pass_context = True, description = "Gives information about a user")
  async def user(self, ctx, *, user: discord.Member = None):
    # prints information about a user

    # grabbing the user's username (defaults to the author if a user was not specified)
    try:
      if user is None:
        user = ctx.author
    except Exception as e:
      embed = discord.Embed(title = "", description = "It doesn't seem like {} is a member of this server. Maybe try mentioning them instead?".format(str(user)))
    else:
      # grabs all of the user's roles (except the default role) and converts it to a string
      roles = []
      for role in user.roles:
        if role.name != "@everyone":
          roles.append(role.name)
      if roles:
        roles = ", ".join(roles)
      else:
        roles = "None"

      if user.nick is not None:
        nick = '(' + user.nick + ')'
      else:
        nick = ""

      # sets user information as the title
      embed = discord.Embed(title = "__**{}**__ {}".format(str(user), nick), description = "**roles:** {}".format(roles), color = user.color)

      # sets the user's avatar as the image (if they have one)
      if user.avatar_url:
        embed.set_thumbnail(url = user.avatar_url)
      else:
        embed.set_thumbnail(url = user.default_avatar_url)

      # displays account age
      embed.add_field(name = "Discord user since:", value = user.created_at.strftime("%d %b %Y"), inline = True)
      embed.add_field(name = "Joined server at:", value = user.joined_at.strftime("%d %b %Y"), inline = True)

      # displays wallet information (if available)
      with open("modules/_data/users.json") as json_data:
        users = json.load(json_data)
      if str(user.id) in users:
        embed.add_field(name = "Balance:", value = "{:,}p".format(users[str(user.id)]["balance"]), inline = True)
        embed.add_field(name = "Slot Winnings:", value = "{:,}p".format(users[str(user.id)]["slot_winnings"]), inline = True)
        embed.add_field(name = "Pennies Stolen:", value = "{:,}p".format(users[str(user.id)]["stolen_money"]), inline = True)

    await ctx.send(embed = embed)

  @commands.command(pass_context = True, description = "Gives information about the current server")
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