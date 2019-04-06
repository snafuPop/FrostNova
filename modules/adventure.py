import discord
from discord.ext import commands
from builtins import bot
from random import randint
from random import choice
import math
from modules.utils import user_json
from titlecase import titlecase

class Adventure(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # grants credits every time a user posts a message
  @commands.Cog.listener()
  async def on_message(self, ctx):
    if (user_json.is_registered(ctx.author)):
      if (ctx.author.id != 547516876851380293):
        # adding 10 credits
        user_json.add_balance(ctx.author, 10)
      user_dict = user_json.get_users()

      # incrementing text posts
      user_dict[str(ctx.author.id)]["text_posts"] = user_dict[str(ctx.author.id)]["text_posts"] + 1
      user_json.update(user_dict)

################################################################################
# adventure
################################################################################

  @commands.command(description = "Go on an adventure!")
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def adventure(self, ctx, *, dungeon: str = None):
    dungeon_dict = user_json.get_dungeons()
    if dungeon is None or titlecase(dungeon) not in dungeon_dict["dungeons"]:
      embed = discord.Embed(title = "", description = "You can explore dungeons by using `!adventure <dungeon name>`, {}.".format(ctx.author.mention))
      embed.set_footer(text = "You can also get a list of dungeons by using !dungeons")
      await ctx.send(embed = embed)
      ctx.command.reset_cooldown(ctx)
      return

    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(ctx.author.mention))
      await ctx.send(embed = embed)
      ctx.command.reset_cooldown(ctx)
      return

    # prepping dicts and keys
    dungeon = titlecase(dungeon)
    user_dict = user_json.get_users()
    user_level = user_dict[str(ctx.author.id)]["level"]
    dungeon_level = dungeon_dict["dungeons"][dungeon]["level"]

    # calculating success rate
    success_rate = int(((user_level - dungeon_level)**3)+90)
    if success_rate < 0:
      success_rate = 0
    elif success_rate > 100:
      success_rate = 100

    random_rate = randint(0,100)
    if random_rate <= success_rate:
      # payout loot!
      loot_table = dungeon_dict["dungeons"][dungeon]["loot"]
      loot_list = self.get_loot(loot_table)
      payout = 0

      # calculating value of all loot
      for loot in loot_list:
        payout = payout + loot_table[loot]
      user_json.add_balance(ctx.author, payout)
      await user_json.add_exp(ctx, ctx.author, dungeon_dict["dungeons"][dungeon]["exp"])


      # creating embed
      embed = discord.Embed(title = "**Adventure successful!**", description = "{} embarked on an adventure to **{}** and succeeded!".format(ctx.author.mention, dungeon), color = ctx.author.color)
      embed.add_field(name = "**Loot found:**", value = ', '.join(loot_list), inline = False)
      embed.add_field(name = "**Payout:**", value = "Sold **{}** piece(s) of loot for **{:,} {}**".format(str(len(loot_list)), payout, user_json.get_currency_name()), inline = False)
    else:
      embed = discord.Embed(title = "**Adventure failed...**", description = "{} embarked on an adventure to **{}** and failed!".format(ctx.author.mention, dungeon), color = ctx.author.color)
      if success_rate == 0:
        embed.add_field(name = "**Forgiveness Cooldown:**", value = "Because your chance to succeed was 0%, your cooldown timer has been reset.")
        ctx.command.reset_cooldown(ctx)

    embed.set_footer(text = "{}% success rate".format(success_rate))
    await ctx.send(embed = embed)


  # returns a list of loot drops
  def get_loot(self, loot_table):
    loot_list = []
    stop = False
    extra_loot = 70
    while not stop:
      pick = choice(list(loot_table))
      loot_list.append(pick)
      if randint(0,100) <= extra_loot:
        extra_loot = extra_loot//2
      else:
        stop = True
    return loot_list


  @commands.command(description = "Returns a list of explorable dungeons.")
  async def dungeons(self, ctx):
    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `!register`".format(ctx.author.mention))
      await ctx.send(embed = embed)
      return

    user_dict = user_json.get_users()
    dungeon_dict = user_json.get_dungeons()
    dungeon_list = list(dungeon_dict["dungeons"])

    embed = discord.Embed(title = "**Explorable Dungeon List**", description = "**{}'s current level:** {:,}".format(ctx.author.mention, user_dict[str(ctx.author.id)]["level"]), color = ctx.author.color)
    low_dungeon = []
    for dungeon in dungeon_list:
      if dungeon_dict["dungeons"][str(dungeon)]["level"]-4 <= user_dict[str(ctx.author.id)]["level"]:
        low_dungeon.append(dungeon)
      #else:
      #  break

    stop = 0
    while len(low_dungeon) >= 1:
      highest = low_dungeon.pop()
      embed.add_field(name = "**{}** (Recommended Level: **{}**)".format(str(highest), dungeon_dict["dungeons"][str(highest)]["level"]), value = "_{}_".format(dungeon_dict["dungeons"][str(highest)]["description"]))
      stop += 1
      if stop == 2:
        break

    if len(low_dungeon) != 0:
      embed.add_field(name = "**Other Dungeons:**", value = "\n".join(low_dungeon))

    await ctx.author.send(embed = embed)


  @adventure.error
  async def cd_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      time_left = int(error.retry_after)
      if time_left >= 3600:
        time_left = time_left//3600
        time_unit = "hour(s)"
      elif time_left >= 60:
        time_left = time_left//60
        time_unit = "minute(s)"
      else:
        time_unit = "second(s)"
      await ctx.send(embed = discord.Embed(title = "", description = "This command is still on cooldown, {}. Try again in {:.0f} {}.".format(ctx.author.mention, time_left, time_unit)))
    else:
      raise error




def setup(bot):
  bot.add_cog(Adventure(bot))