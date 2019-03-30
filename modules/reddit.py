import discord
from discord.ext import commands
from builtins import bot

from random import randint
from random import choice
import praw
import json

from prawcore import NotFound
import mimetypes
import urllib

with open("_config/settings.json") as json_data:
  data = json.load(json_data)
r = praw.Reddit(client_id = data["REDDIT_CLIENT_ID"], client_secret = data["REDDIT_CLIENT_SECRET"], user_agent = data["REDDIT_USER_AGENT"])

class Reddit(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.command(description = "Grabs a random image from a defined subreddit. Only pulls from the 100 hottest posts.")
  async def reddit(self, ctx, *, sub: str = "all"):
    # pulls a submission randomly from the 100 hottest posts from a specified subreddit.

    # sanitizing input
    sub = sub.replace(" ", "_")

    # restricts nsfw posts from being posted in non-nsfw channels
    if (r.subreddit(sub)).over18 and not ctx.channel.is_nsfw():
      embed = discord.Embed(title = "", description = "There are kids here {}! I can only submit posts from NSFW subreddits in text channels marked NSFW.".format(ctx.author.mention))
    else:
      # enumerates 100 hottest posts
      post = list(r.subreddit(sub).hot(limit = 100))

      # if list is empty, then the subreddit does not exist
      if not post:
        embed = discord.Embed(title = "", description = "Could not find **/r/{}**, {}.".format(sub, ctx.author.mention))

      # creates an embed message for the reddit post
      else:
        post = choice(post)

        # if the post is tagged as a spoiler, then the content will be wrapped by spoiler tags
        title = post.title
        text = post.selftext
        if post.spoiler:
          title = "||{}||".format(title)
          text = "||{}||".format(text)

        embed = discord.Embed(title = title, description = text, color = ctx.author.color)
        embed.set_author(name = post.author.name, url = post.shortlink, icon_url = post.author.icon_img)
        embed.set_footer(text = "Random post from /r/{}\n {:-2}% upvoted".format(sub, post.upvote_ratio*100))
        embed.set_image(url = post.url)
    await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(Reddit(bot))