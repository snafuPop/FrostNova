import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

class Poll(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.poll_emotes = [
        "<:poll_red:603005685172666387>",
        "<:poll_blue:603005674997153793>",
        "<:poll_yellow:603005694056333322>",
        "<:poll_green:603005118111154176>",
        "<:poll_purple:603005719062773761>",
        "<:poll_orange:603005944640700446>",
        "<:poll_teal:603006203219410944>",
        "<:poll_gray:603005956883873852>"]


  poll = app_commands.Group(name = "poll", description = "Commands that begins a poll in the current text channel")

  @poll.command(name = "yesno", description = "Asks a simple yes/no question in the current text channel")
  @app_commands.describe(question = "The topic of the poll")
  async def start_yesno(self, interaction: discord.Interaction, question: str):
    embed = discord.Embed(title = "")
    embed.set_author(name = question, icon_url = interaction.user.display_avatar.url)
    await interaction.response.send_message(embed = embed)
    message = await interaction.original_response()
    await message.add_reaction("<:agree:603662870567190597>")
    await message.add_reaction("<:disagree:603662870365995019>")


  @poll.command(name = "survey", description = "Begins a poll in the current text channel with a list of defined answers to pick from.")
  @app_commands.describe(question = "The topic of the poll", options = "A list of up to 8 answers that users can choose from, separated by a semi-colon (;)")
  async def start_survey(self, interaction: discord.Interaction, question: str, options: str):
    options = options.split(";")

    if len(options) < 2 or len(options) > 8:
      message = "There must be at least 2 options and at most 8 options provided."
      embed = self.bot.create_error_response(message = message)
      embed.add_field(name = "For example:", value =  "`\\poll survey vanilla;strawberry;chocolate`")
      await interaction.response.send_message(embed = embed, ephemeral = True)
      return

    embed = discord.Embed(title = "")
    embed.set_author(name = question, icon_url = interaction.user.display_avatar.url)

    choices_text = []
    for i in range(len(options)):
      choices_text.append(f"{self.poll_emotes[i]} {options[i]}")
    embed.add_field(name = "**Choices:**", value = "\n".join(choices_text))

    await interaction.response.send_message(embed = embed)

    for i in range(len(options)):
      message = await interaction.original_response()
      await message.add_reaction(self.poll_emotes[i])


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Poll(bot))