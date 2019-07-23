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
  @commands.command(aliases = ["vote"], description = "Start a poll.")
  async def poll(self, ctx, *, options: str = "None"):
    options = options.split(";")
    topic = options.pop(0)
    if len(options) < 2 or len(options) > 8:
      await ctx.send(embed = discord.Embed(title = "", description = "You can create a poll by using `{}poll <topic;option 1;option 2;...>`. You need at least **2** (at most **8** options) to choose from.".format(ctx.prefix)))
    else:
      embed = discord.Embed(title = "**Poll started!**", description = "Started by {}".format(ctx.author.mention))

      # populating choices
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


  @commands.command(description = "test")
  async def get_msg(self, ctx, msg_id):
    await ctx.send(msg_id)
    message = await ctx.channel.fetch_message(msg_id)
    for emoji in message.reactions:
      await ctx.send(emoji)

def setup(bot):
  bot.add_cog(Poll(bot))