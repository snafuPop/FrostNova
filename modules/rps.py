import discord
from discord.ext import commands
from builtins import bot
import random
from modules.utils import user_json

class Rps(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.move_list = {
      "rock": ":fist:",
      "paper": ":raised_hand:",
      "scissors": ":v:"}

  @commands.command(aliases = ["rochambeau"], description = "Play rock-paper-scissors against me!")
  async def rps(self, ctx, user_move: str = None, bid: str = None):
    try:
      bid = await user_json.can_do(ctx, ctx.author, bid)
    except:
      await ctx.send(embed = discord.Embed(title = "", description = "You can start a rock-paper-scissor game with me by typing `!rps <rock, paper, or scissors> <bet>`, {}.".format(ctx.author.mention)))
      return

    if user_move not in self.move_list.keys():
      await ctx.send(embed = discord.Embed(title = "", description = "You can start a rock-paper-scissor game with me by typing `!rps <rock, paper, or scissors> <bet>`, {}.".format(ctx.author.mention)))
      return

    # choosing the bot's move
    bot_move = random.choice(list(self.move_list))

    # grabbing initial bet
    initial_money = user_json.get_balance(ctx.author)

    # end conditions
    output = ["", ""]
    if user_move == bot_move:
      output[0] = "It's a tie!"
      output[1] = "Your bet is returned."
      bid = 0
    elif (user_move == "rock" and bot_move == "scissors") or (user_move == "paper" and bot_move == "rock") or (user_move == "scissors" and bot_move == "paper"):
      output[0] = "{} won!".format(ctx.author.name)
      output[1] = "You earned your bet!"
    else:
      output[0] = "{} lost!".format(ctx.author.name)
      output[1] = "You lost your bet!"
      bid = -bid

    user_json.add_balance(ctx.author, bid)
    embed = discord.Embed(title = output[0], description = "{} {} :boom: {}".format(ctx.author.mention, self.move_list[user_move], self.move_list[bot_move]))
    embed.add_field(name = "Payout:", value = "{}\n{:,} ⮕ {:,} {}".format(output[1], initial_money, user_json.get_balance(ctx.author), user_json.get_currency_name()), inline = False)
    await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(Rps(bot))