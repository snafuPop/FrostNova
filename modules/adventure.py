import discord
from discord.ext import commands
from builtins import bot
from random import randint
from random import choice
import math
from modules.utils import user_json
from titlecase import titlecase
from operator import itemgetter

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
      if user_dict[str(ctx.author.id)]["username"] != ctx.author.name:
        user_dict[str(ctx.author.id)]["username"] = ctx.author.name
      user_json.update(user_dict)


  @commands.command(aliases = ["adv", "expore", "go"], description = "Go on an adventure!")
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def adventure(self, ctx, *, dungeon: str = None):
    dungeon_dict = user_json.get_dungeons()
    if dungeon is None or titlecase(dungeon) not in dungeon_dict["dungeons"]:
      embed = discord.Embed(title = "", description = "You can explore dungeons by using `{}adventure <dungeon name>`, {}.".format(ctx.prefix, ctx.author.mention))
      embed.set_footer(text = "You can also get a list of dungeons by using !dungeons")
      await ctx.send(embed = embed)
      ctx.command.reset_cooldown(ctx)
      return

    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `{}register`".format(ctx.author.mention, ctx.prefix))
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

    # if the adventure is successful
    if random_rate <= success_rate:
      # payout loot!
      loot_table = dungeon_dict["dungeons"][dungeon]["loot"]
      loot_list = self.get_loot(loot_table)
      payout = 0

      # calculating value of all loot
      for loot in loot_list:
        payout = payout + loot_table[loot]
      user_json.add_balance(ctx.author, payout)
      exp = dungeon_dict["dungeons"][dungeon]["exp"]
      await user_json.add_exp(ctx, ctx.author, exp)


      # creating embed
      embed = discord.Embed(title = "**Adventure successful!**", description = "{} embarked on an adventure to **{}** and succeeded!".format(ctx.author.mention, dungeon), color = ctx.author.color)
      embed.add_field(name = "**Loot found:**", value = ', '.join(loot_list), inline = False)
      embed.add_field(name = "**Results:**", value = "Sold **{:,}** piece(s) of loot for **{:,} {}**\nGained **{:,}** exp".format(len(loot_list), payout, user_json.get_currency_name(), exp) , inline = False)
      user_json.add_loot_earnings(ctx.author, payout)

    # if the adventure failed
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
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `{}register`".format(ctx.author.mention, ctx.prefix))
      await ctx.send(embed = embed)
      return

    # preparing dicts
    user_dict = user_json.get_users()
    dungeon_dict = user_json.get_dungeons()
    dungeon_list = list(dungeon_dict["dungeons"])

    # goes through the dictionary of dungeons and only grabs dungeons whose levels are no more than 4 higher than the player's
    embed = discord.Embed(title = "**Explorable Dungeon List**", description = "**{}'s current level:** {:,}".format(ctx.author.mention, user_dict[str(ctx.author.id)]["level"]), color = ctx.author.color)
    dungeon_name = ""
    dungeon_level = 0
    low_dungeon = []
    for dungeon in dungeon_list:
      if dungeon_dict["dungeons"][str(dungeon)]["level"]-4 <= user_dict[str(ctx.author.id)]["level"]:
        dungeon_name = dungeon
        dungeon_level = dungeon_dict["dungeons"][str(dungeon)]["level"]
        low_dungeon.append([dungeon_name, dungeon_level])

    # because dicts are unsorted, we have to sort it ourselves
    dungeons = sorted(low_dungeon, key = lambda x: x[1])

    # gives detailed informatinon for the 2 highest level dungeons
    stop = 0
    while dungeons:
      highest = dungeons.pop()
      embed.add_field(name = "**{}** (Recommended Level: **{:,}**)".format(highest[0], highest[1]), value = "_{}_".format(dungeon_dict["dungeons"][highest[0]]["description"]))
      stop += 1
      if stop == 2:
        break

    # simply gives the names of other dungeons
    if dungeons:
      other_dungeons = ""
      for dungeon in dungeons:
        other_dungeons = other_dungeons + "{}\n".format(dungeon[0])
      embed.add_field(name = "**Other Dungeons:**", value = other_dungeons)

    await ctx.author.send(embed = embed)


  # helper function for calculating the cost of upgrading an item
  def calculate_item_upgrade(self, level):
    return math.ceil(level**2.79+100)


  @commands.command(description = "Upgrades your item level.")
  async def upgrade(self, ctx, *, num_of_upgrades: str = None):
    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the sytem, {}. Try `{}register`".format(ctx.author.mention, ctx.prefer))
      await ctx.send(embed = embed)
      return

    user_dict = user_json.get_users()
    user_level = user_dict[str(ctx.author.id)]["level"]

    # user level isn't high enough to perform upgrades
    if user_level < 30:
      embed = discord.Embed(title = "**Level Too Low!**", description = "Hmmm, it doesn't seem like you're strong enough to handle an upgraded weapon. Come back when you're at least level 30.", color = ctx.author.color)
      embed.set_footer(text = "(You're currently level {})".format(user_level))
      embed.set_thumbnail(url = "https://wiki.mabinogiworld.com/images/2/25/Ferghus.png")
      await ctx.send(embed = embed)
      return

    user_item_level = user_dict[str(ctx.author.id)]["item_level"]
    user_balance = user_dict[str(ctx.author.id)]["balance"]

    # checks the cost of upgrading
    if num_of_upgrades == None:
      embed = discord.Embed(title = "**Item Upgrading**", description = "Are you interested in upgrading your item's level, {}? Right now your item level is {}, but I can increase it for you, for a small fee of course. If you'd like me to upgrade your item once, use `{}upgrade once`. Or, I can upgrade your item as many times as I can with `{}upgrade max`.".format(ctx.author.mention, user_item_level, ctx.prefix, ctx.prefix))
      embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Cost of One Upgrade:**", value = "{:,} {}".format(self.calculate_item_upgrade(user_item_level+1), user_json.get_currency_name()))
      embed.set_thumbnail(url = "https://wiki.mabinogiworld.com/images/2/25/Ferghus.png")
      await ctx.send(embed = embed)
      return

    # calculate cost of upgrades
    elif num_of_upgrades in ["once", "max"]:
      upgrade_cost = 0
      if num_of_upgrades == "once":
        upgrade_cost = self.calculate_item_upgrade(user_item_level+1)
        if upgrade_cost > user_balance:
          embed = discord.Embed(title = "**Item Upgrading**", description = "Sorry, {}, I don't give credit! Come back when you're a little... mmm... richer!".format(ctx.author.mention))
          embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
          embed.add_field(name = "**Cost of One Upgrade:**", value = "{:,} {}".format(upgrade_cost, user_json.get_currency_name()))
          embed.set_thumbnail(url = "https://wiki.mabinogiworld.com/images/2/25/Ferghus.png")
          await ctx.send(embed = embed)
          return
        else:
          final_item_level = user_item_level + 1
          final_balance = user_balance - upgrade_cost
      else:
        i = 1
        while True:
          add_upgrade_cost = self.calculate_item_upgrade(user_item_level+i)
          if upgrade_cost + add_upgrade_cost <= user_balance:
            upgrade_cost += self.calculate_item_upgrade(user_item_level+i)
            i += 1
          else:
            break
        final_item_level = user_item_level + i
        final_balance = user_balance - upgrade_cost

      # sending the final message
      user_dict[str(ctx.author.id)]["item_level"] = final_item_level
      user_dict[str(ctx.author.id)]["balance"] = final_balance
      embed = discord.Embed(title = "**Item Upgrading**", description = "There you go, {}! Your item is now level **{:,}**.".format(ctx.author.mention, final_item_level))
      embed.add_field(name = "**Your Original Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(final_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Total Upgrade Costs:**", value = "{:,} {}".format(upgrade_cost, user_json.get_currency_name()))
      embed.set_thumbnail(url = "https://wiki.mabinogiworld.com/images/2/25/Ferghus.png")
      await ctx.send(embed = embed)
      user_json.update(user_dict)
      return

    else:
      embed = discord.Embed(title = "**Item Upgrading**", description = "I'm not quite sure what you said there, {}. If you'd like me to upgrade your item once, use `{}upgrade once`. Or, I can upgrade your item as many times as I can with `{}upgrade max`.".format(ctx.author.mention, ctx.prefix, ctx.prefix))
      await ctx.send(embed = embed)
      return





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