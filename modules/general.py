import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from ButtonPaginator import Paginator
from builtins import bot, guild_ids
from modules.utils import user_json
from random import randint

class General(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  # ping pong!
  @cog_ext.cog_slash(name = "wave", description = "Checks the status of the bot.", guild_ids = guild_ids)
  async def hello(self, ctx):
    embed = discord.Embed(title = "", description = "Hi, {}! :wave:".format(ctx.author.mention))
    embed.set_footer(text = "{}ms response time".format(round(bot.latency*1000)))
    await ctx.send(embed = embed)


  @cog_ext.cog_slash(name = "leaderboard", description = "Gets leaderboard information.", guild_ids = guild_ids)
  async def leaderboard(self, ctx):
    await ctx.defer()

    embeds = []
    embeds.append(self.top_five("balance", "Wealthiest Users"))
    embeds.append(self.top_five("level", "Highest Levels"))
    embeds.append(self.top_five("item_level", "Strongest Item Levels"))
    embeds.append(self.top_five("damage_dealt", "Heftiest Damage Dealers"))

    paginated_embed = Paginator(bot = self.bot, ctx = ctx, embeds = embeds, only = ctx.author)
    await paginated_embed.start()


  # # helper method to append a field that contains leaderboard information
  def top_five(self, parameter, title):
    medals = [":first_place:", ":second_place:", ":third_place:", ":medal:", ":military_medal:"]

    users = user_json.get_users()
    user_list = sorted(users, key = lambda x: (users[x][parameter]), reverse = True)
    #user_list.remove("702671392973389954") # hiding y'shtola from the list
    top_users = ""
    for i in range(len(medals)):
      top_users += "\u3164{} **{}**: {:,}\n".format(medals[i], users[user_list[i]]['username'], users[user_list[i]][parameter])
    embed = discord.Embed(title = title, description = top_users)
    embed.set_thumbnail(url = "https://4.bp.blogspot.com/-h_NjR_vNLQI/XDG00QSYerI/AAAAAAABQ8A/5jqs8mFNZEU-rcSmEuDykk2LstHaDpwLQCLcBGAs/s800/game_kyoutai_man.png")
    embed.set_footer(text = "Only registered users are tracked. Type /register to start tracking your records (and more)!")

    return embed


def setup(bot):
  bot.add_cog(General(bot))