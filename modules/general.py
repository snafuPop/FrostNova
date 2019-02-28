import discord
from discord.ext import commands
from builtins import bot

@bot.command(description = "Checks the status of the bot")
async def hello():
  embed = discord.Embed(title = "", description = ":wave:")
  await bot.say(embed = embed)

@bot.command(pass_context = True, description = "Hugs a user")
async def hug(ctx, *, user: discord.Member = None):
  if user is None:
    embed = discord.Embed(title = "", description = "Let me know who to hug by typing in `!hug <user>`")
  else:
    embed = discord.Embed(title = "", description = "{} -> (つ≧▽≦)つ {}".format(ctx.message.author.mention, user.mention), color = ctx.message.author.color)

  await bot.say(embed = embed)


@bot.command(description = "Gives information about the bot")
async def about():
  embed = discord.Embed(title = " ", color = 0x0080ff)
  embed.set_author(name = "Y'shtola Bot", url = "https://github.com/snafuPop/yshtola", icon_url = "https://image.flaticon.com/icons/png/512/25/25231.png")
  embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/482726823776485392/548612049953882143/rhuul.png")
  embed.add_field(name = "Author", value = "snafuPop#0007", inline = True)
  embed.add_field(name = "Language", value = "Python 3.6.x", inline = True)
  embed.set_footer(text = "Use !help to produce a list of commands")
  await bot.say(embed = embed)
