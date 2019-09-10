import discord
from discord.ext import commands
from builtins import bot
import json
import aiohttp

class Final_Fantasy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    with open("/home/snafuPop/yshtola/_config/settings.json") as json_data:
      self.api_key = json.load(json_data)["FFLOGS_API_KEY"]

  async def character_lookup(self, name, server):
    url = "https://xivapi.com/character/search?name={}&server={}".format(name, server)
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          return await response.json()
    except Exception as error:
      print("Request failed: {}".format(error), flush = True)

  @commands.command(aliases = ["log"], description = "Grabs some information about a player from FFLogs")
  async def fflogs(self, ctx, *args):
    await ctx.trigger_typing()
    if len(args) != 3:
      await ctx.send(embed = discord.Embed(title = "", description = "You can request information about someone's FFLogs by using `{}fflogs <first-name> <last-name> <server>`, {}.".format(ctx.prefix, ctx.author.mention)))
      return

    url = "https://www.fflogs.com:443/v1/rankings/character/{}%20{}/{}/na?partition=1&api_key={}".format(args[0], args[1], args[2], self.api_key)
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          user = await response.json()
    except Exception as error:
      await ctx.send(embed = discord.Embed(title = "", description = "Request failed: {}".format(error)))

    if 'status' in user and 'error' in user:
      await ctx.send(embed = discord.Embed(title = "Error Code: {}".user["status"], description = user["error"]))
      return

    embed = discord.Embed(title = "**FFLogs Report for {} of {}**".format(user[0]["characterName"], user[0]["server"]), description = "Requested by {}".format(ctx.author.mention), color = ctx.author.color)
    data = ""
    for encounter in user:
      job_icon = discord.utils.get(self.bot.emojis, name = encounter["spec"].replace(" ", ""))
      percentile = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
      data += "\u3164{} **{}:** {} (**{}** percentile) ([Report](https://www.fflogs.com/reports/{}#fight=last))\n".format(job_icon, encounter["encounterName"], encounter["total"], percentile(encounter["percentile"]), encounter["reportID"])
    embed.add_field(name = "**Historical Reports** (Patch {})".format(user[0]["ilvlKeyOrPatch"]), value = data)
    embed.add_field(name = "**User Page:**", value = "\u3164https://www.fflogs.com/character/id/{}".format(user[0]["characterID"]))

    thumbnail = (await self.character_lookup(user[0]["characterName"], user[0]["server"]))
    thumbnail = thumbnail["Results"][0]["Avatar"]
    embed.set_thumbnail(url = thumbnail)
    await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(Final_Fantasy(bot))