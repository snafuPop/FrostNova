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
    self.npc = {"adventure": "https://wiki.mabinogiworld.com/images/4/41/Meriel.png",
                "upgrade": "https://wiki.mabinogiworld.com/images/2/25/Ferghus.png",
                "raid": "https://wiki.mabinogiworld.com/images/3/39/Odran.png"}

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

  def set_msg_thumbnail(self, embed, context):
    embed.set_thumbnail(url = self.npc[context])


  def get_list_of_dungeons(self, dungeon_dict, user_level):
    dungeon_name = ""
    dungeon_level = 0
    dungeons = []
    dungeon_list = list(dungeon_dict["dungeons"])
    for dungeon in dungeon_list:
      dungeon_name = dungeon
      dungeon_level = dungeon_dict["dungeons"][str(dungeon)]["level"]
      if dungeon_level-4 <= user_level:
        dungeons.append([dungeon_name, dungeon_level])
    return sorted(dungeons, key = lambda x: x[1])


  def get_dungeon_success_rate(self, user_level, dungeon_level):
    success_rate = int(((user_level - dungeon_level)**3)+90)
    return 100 if success_rate > 100 else success_rate


  @commands.command(description = "Returns a list of explorable dungeons.")
  async def dungeons(self, ctx):
    user_dict = user_json.get_users()
    dungeon_dict = user_json.get_dungeons()
    dungeon_list = list(dungeon_dict["dungeons"])

    # goes through the dictionary of dungeons and only grabs dungeons whose levels are no more than 4 higher than the player's
    embed = discord.Embed(title = "**Explorable Dungeon List**", description = "**{}'s current level:** {:,}".format(ctx.author.mention, user_dict[str(ctx.author.id)]["level"]), color = ctx.author.color)
    
    user_level = user_dict[str(ctx.author.id)]["level"]
    dungeons = self.get_list_of_dungeons(dungeon_dict, user_level)

    # gives detailed informatinon for the 2 highest level dungeons
    stop = 0
    while dungeons:
      highest = dungeons.pop()
      embed.add_field(name = "**{}** (Lv. **{}**)\n(Success Rate: **{:,}%**)".format(highest[0], highest[1], self.get_dungeon_success_rate(user_level, highest[1])), value = "_{}_".format(dungeon_dict["dungeons"][highest[0]]["description"]))
      stop += 1
      if stop == 2:
        break

    # simply gives the names of other dungeons
    if dungeons:
      other_dungeons = ""
      for dungeon in dungeons:
        other_dungeons = other_dungeons + "*{}* (Lv. **{}**)\n".format(dungeon[0], dungeon[1])
      embed.add_field(name = "**Other Dungeons:**", value = other_dungeons)

    await ctx.send(embed = embed)
    ctx.command.reset_cooldown(ctx)
    return



  @commands.command(aliases = ["adv", "expore", "go"], description = "Go on an adventure!", cooldown_after_parsing = True)
  @commands.cooldown(1, 1800, commands.BucketType.user)
  async def adventure(self, ctx, *, dungeon: str = None):
    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the system, {}. Try `{}register`".format(ctx.author.mention, ctx.prefix))
      await ctx.send(embed = embed)
      ctx.command.reset_cooldown(ctx)
      return

    dungeon_dict = user_json.get_dungeons()
    if dungeon is None or titlecase(dungeon) not in dungeon_dict["dungeons"]:
      embed = discord.Embed(title = "**Adventuring**", description = "Hmmm... I don't think that's the name of any dungeon I heard of, {}. You can see which dungeons you can go to by using `{}dungeons`.".format(ctx.author.mention, ctx.prefix), color = ctx.author.color)
      self.set_msg_thumbnail(embed, "adventure")
      await ctx.send(embed = embed)
      ctx.command.reset_cooldown(ctx)
      return

    # prepping dicts and keys
    dungeon = titlecase(dungeon)
    user_dict = user_json.get_users()
    user_level = user_dict[str(ctx.author.id)]["level"]
    dungeon_level = dungeon_dict["dungeons"][dungeon]["level"]

    # calculating success rate
    success_rate = self.get_dungeon_success_rate(user_level, dungeon_level)
    if success_rate < 0:
      success_rate = 0
    elif success_rate > 100:
      success_rate = 100

    random_rate = randint(0,100)

    # if the adventure is successful
    if random_rate <= success_rate:
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
    self.set_msg_thumbnail(embed, "adventure")
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



  # helper function for calculating the cost of upgrading an item
  def calculate_item_upgrade(self, level):
    return math.ceil(level**6.94+100)



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
      embed = discord.Embed(title = "**Level Too Low!**", description = "Hmmm, it doesn't seem like you're strong enough to handle an upgraded weapon. Come back when you're at least **level 30.**", color = ctx.author.color)
      embed.set_footer(text = "(You're currently level {})".format(user_level))
      self.set_msg_thumbnail(embed, "upgrade")
      await ctx.send(embed = embed)
      return

    user_item_level = user_dict[str(ctx.author.id)]["item_level"]
    user_balance = user_dict[str(ctx.author.id)]["balance"]

    # checks the cost of upgrading
    if num_of_upgrades == None:
      embed = discord.Embed(title = "**Item Upgrading**", description = "Are you interested in upgrading your item's level, {}? Right now your item level is **{:,}**, but I can increase it for you, for a small fee of course. If you'd like me to upgrade your item once, use `{}upgrade once`. Or, I can upgrade your item as many times as I can with `{}upgrade max`.".format(ctx.author.mention, user_item_level, ctx.prefix, ctx.prefix), color = ctx.author.color)
      embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Cost of One Upgrade:**", value = "{:,} {}".format(self.calculate_item_upgrade(user_item_level+1), user_json.get_currency_name()))
      self.set_msg_thumbnail(embed, "upgrade")
      await ctx.send(embed = embed)
      return

    # calculate cost of upgrades
    elif num_of_upgrades in ["once", "max"]:
      upgrade_cost = 0
      if num_of_upgrades == "once":
        upgrade_cost = self.calculate_item_upgrade(user_item_level+1)
        if upgrade_cost > user_balance:
          embed = discord.Embed(title = "**Item Upgrading**", description = "Sorry, {}, I don't give credit! Come back when you're a little... mmm... richer!".format(ctx.author.mention), color = ctx.author.color)
          embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
          embed.add_field(name = "**Cost of One Upgrade:**", value = "{:,} {}".format(upgrade_cost, user_json.get_currency_name()))
          self.set_msg_thumbnail(embed, "upgrade")
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
        if upgrade_cost == 0:
          embed = discord.Embed(title = "**Item Upgrading**", description = "Sorry, {}, I don't give credit! Come back when you're a little... mmm... richer!".format(ctx.author.mention), color = ctx.author.color)
          embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
          embed.add_field(name = "**Cost of One Upgrade:**", value = "{:,} {}".format(upgrade_cost, user_json.get_currency_name()))
          self.set_msg_thumbnail(embed, "upgrade")
          await ctx.send(embed = embed)
          return
        final_item_level = user_item_level + i
        final_balance = user_balance - upgrade_cost

      # sending the final message
      user_dict[str(ctx.author.id)]["item_level"] = final_item_level
      user_dict[str(ctx.author.id)]["balance"] = final_balance
      embed = discord.Embed(title = "**Item Upgrading**", description = "There you go, {}! Your item is now level **{:,}**.".format(ctx.author.mention, final_item_level), color = ctx.author.color)
      embed.add_field(name = "**Your Original Balance:**", value = "{:,} {}".format(user_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Your Current Balance:**", value = "{:,} {}".format(final_balance, user_json.get_currency_name()))
      embed.add_field(name = "**Total Upgrade Costs:**", value = "{:,} {}".format(upgrade_cost, user_json.get_currency_name()))
      self.set_msg_thumbnail(embed, "upgrade")
      await ctx.send(embed = embed)
      user_json.update(user_dict)
      return

    else:
      embed = discord.Embed(title = "**Item Upgrading**", description = "I'm not quite sure what you said there, {}. If you'd like me to upgrade your item once, use `{}upgrade once`. Or, I can upgrade your item as many times as I can with `{}upgrade max`.".format(ctx.author.mention, ctx.prefix, ctx.prefix), color = ctx.author.color)
      self.set_msg_thumbnail(embed, "upgrade")
      await ctx.send(embed = embed)
      return

  @commands.command(description = "Embark on a raid!")
  async def raid(self, ctx, *, dungeon: str = None):
    if not user_json.is_registered(ctx.author):
      embed = discord.Embed(title = "", description = "It looks like you aren't registered in the sytem, {}. Try `{}register`".format(ctx.author.mention, ctx.prefer))
      await ctx.send(embed = embed)
      return

    user_dict = user_json.get_users()
    user_level = user_dict[str(ctx.author.id)]["level"]
    user_item_level = user_dict[str(ctx.author.id)]["item_level"]

    # user level isn't high enough to embark on a raid
    if user_level < 30:
      embed = discord.Embed(title = "**Level Too Low!**", description = "You think I'll let a whelp like you embark on a raid, {}? Come back when you're a little stronger - say, **level 30**.".format(ctx.author.mention), color = ctx.author.color)
      embed.set_footer(text = "(You're currently level {})".format(user_level))
      self.set_msg_thumbnail(embed, "raid")
      await ctx.send(embed = embed)
      return

    # print help information if no dungeon specified
    if dungeon == None:
      embed = discord.Embed(title = "**Raid**", description = "So you're interested in embarking on a **raid**, {}? Raids are special dungeons that uses your **item level** stat instead of your level in order to determine how much loot you receive. The higher your item level, the more monsters you'll potentially be able to kill. If it's high enough, you may be strong enough to kill the boss of the area! Of course, you'll also get EXP and I can only take you on a raid every **12 hours**.\n\nYou can check your item level either by using `{}user` or `{}upgrade`. Once you think you're ready, you can use `{}raid <name of raid zone>` to begin a raid.".format(ctx.author.mention, ctx.prefix, ctx.prefix, ctx.prefix), color = ctx.author.color)
      embed.add_field(name = "**Your Current Item Level:**", value = "{:,}".format(user_item_level))
      embed.add_field(name = "**Available Raid Zones:**", value = "{:,} {}".format(self.calculate_item_upgrade(user_item_level+1), user_json.get_currency_name()))
      self.set_msg_thumbnail(embed, "raid")
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