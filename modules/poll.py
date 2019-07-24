import discord
from discord.ext import commands

class Poll(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.num = [
        "<:poll_red:603005685172666387>",
        "<:poll_blue:603005674997153793>",
        "<:poll_yellow:603005694056333322>",
        "<:poll_green:603005118111154176>",
        "<:poll_purple:603005719062773761>",
        "<:poll_orange:603005944640700446>",
        "<:poll_teal:603006203219410944>",
        "<:poll_gray:603005956883873852>"]

  # polling!
  @commands.command(aliases = ["vote"], description = "Start a poll. You can leave options blank in order to start a Yes/No vote instead.")
  async def poll(self, ctx, *, options: str = "None"):
    options = options.split(";")
    topic = options.pop(0)
    if topic is "None" or len(options) == 1 or len(options) > 8:
      await ctx.send(embed = discord.Embed(title = "", description = "You can create a poll by using `{}poll <topic;option 1;option 2;...>`. Leave options blank if you want to start a Yes/No vote.".format(ctx.prefix)))
    else:
      embed = discord.Embed(title = "**Poll started!**", description = "Started by {}".format(ctx.author.mention))

      if len(options) != 0:
        choices = []
        for i in range (0, len(options)):
          choice_line = self.num[i] + " "+ options[i]
          choices.append(choice_line)
        embed.add_field(name = "**__{}__**".format(topic), value = "\n".join(choices))
        embed.set_thumbnail(url = "https://cdn4.iconfinder.com/data/icons/universal-icons-4/512/poll-512.png")
        poll_msg = await ctx.send(embed = embed)

        # adding reactions
        for i in range (0, len(options)):
          await poll_msg.add_reaction(self.num[i])

      else:
        embed.add_field(name = "**__{}__**".format(topic), value = "Vote yes or no below.")
        embed.set_thumbnail(url = "https://cdn4.iconfinder.com/data/icons/universal-icons-4/512/poll-512.png")
        poll_msg = await ctx.send(embed = embed)

        await poll_msg.add_reaction("<:agree:603662870567190597>")
        await poll_msg.add_reaction("<:disagree:603662870365995019>")

def setup(bot):
  bot.add_cog(Poll(bot))