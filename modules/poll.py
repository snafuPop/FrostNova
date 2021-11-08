import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids

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
  @cog_ext.cog_slash(name = "poll", description = "Start a poll. You can leave options blank in order to start a Yes/No vote instead.",
    options = [create_option(
      name = "question",
      description = "A question you want to ask about.",
      option_type = 3,
      required = True),
    create_option(
      name = "options",
      description = "List of options, separated by a semi-colon (;).",
      option_type = 3,
      required = False)])
  async def poll(self, ctx, *, question: str = None, options: str = None):
    embed = discord.Embed(title = "")
    embed.set_author(name = question, icon_url = ctx.author.avatar_url)

    # create yes/no poll
    if options == None:
      poll_msg = await ctx.send(embed = embed)
      await poll_msg.add_reaction("<:agree:603662870567190597>")
      await poll_msg.add_reaction("<:disagree:603662870365995019>")


    # create a standard poll
    else:
      options = options.split(";")

      if len(options) == 1:
        await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: You cannot provide only one option."))
        return

      if len(options) > 8:
        await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: You can only provide at most eight options."))
        return

      choices_text = []
      for i in range(0, len(options)):
        choices_text.append("{} {}".format(self.num[i], options[i])) 
      embed.add_field(name = "**Choices:**", value = "\n".join(choices_text))
      poll_msg = await ctx.send(embed = embed)
      for i in range(0, len(options)):
        await poll_msg.add_reaction(self.num[i])


def setup(bot):
  bot.add_cog(Poll(bot))