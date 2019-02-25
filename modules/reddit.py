import discord
from discord.ext import commands
from builtins import bot

from random import randint
from random import choice
import praw
import json

with open("_config/settings.json") as json_data:
  data = json.load(json_data)

reddit = praw.Reddit(client_id = data["REDDIT_CLIENT_ID"], client_secret = data["REDDIT_CLIENT_SECRET"], user_agent = data["REDDIT_USER_AGENT"])

def makeColor():
  # genereates a random color  
  colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
  colour = int(colour, 16)
  return colour

@bot.command(pass_context = True, aliases=["reddit"])
async def __reddit(ctx, *, sub: str = None):

  if sub is None:
    embed = discord.Embed(title ="", description = "Try parsing a subreddit with `!reddit <subreddit name>`, {}".format(ctx.message.author.mention), color = 0xe74c3c)
  else:
    sub = sub.replace(" ", "_")
    posts = reddit.subreddit(sub).hot(limit=50)
    post_choose = randint(0,50)

    for i, post in enumerate(posts):
      if i == post_choose:
        title = post.title
        url = post.url
        break

    embed = discord.Embed(title = "Random post from /r/{}".format(sub), description = "Requested by {}".format(ctx.message.author.mention), color=makeColor())
    embed.set_footer(text = title, icon_url = "https://i.imgur.com/BWZxWkG.png")
    embed.set_image(url = url)
  await bot.say(embed = embed)