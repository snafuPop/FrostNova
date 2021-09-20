import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from builtins import bot, guild_ids

from random import randint
from random import choice
from enum import Enum

class Drops(Enum):
  CRYSTAL_SHARD = "<:crystal_shard:888531512461508628>"
  CRYSTAL_ARMOR_SEED = "<:crystal_armour_seed:888531512209866824>"
  CRYSTAL_WEAPON_SEED = "<:crystal_weapon_seed:888531512394383370>"
  ENHANCED_CRYSTAL_WEAPON_SEED = "<:enhanced_crystal_weapon_seed:888531512201449542>"
  YOUNLLEF = "<:younllef:888531512591527997>"

class Random(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # rolls a random number between 1 and a user defined max (defaults to 100)
  # also optionally takes in a string input
  @cog_ext.cog_slash(name = "roll", description = "Rolls a dice.", guild_ids = guild_ids, 
    options = [create_option(
      name = "number",
      description = "The highest possible number you can roll. Leave blank for 100.",
      option_type = 4,
      required = False),
    create_option(
      name = "declaration",
      description = "Attaches a declaration to your outcome.",
      option_type = 3,
      required = False)]
    )
  async def roll(self, ctx, number: int = 100, declaration: str = ""):
    if number <= 1:
      await ctx.send(embed = discord.Embed(title = "", description = ":no_entry: Maybe roll a value greater than 1, {}? (｀Д´)".format(ctx.author.mention)))
      return

    # rolls a bonus modifier that determines the appearance of special dice or not
    dice = ":diamond_shape_with_a_dot_inside:" if 1 == randint(1,1000000) else ":game_die:"

    # creates the embed message
    result = randint(1, number)
    embed = discord.Embed(title = "", description = "{} {} rolled a **{:,}**! {}".format(dice, ctx.author.mention, result, dice), color = ctx.author.color)
    embed.set_footer(text = "...out of {:,}".format(number))

    # parses the declaration
    if declaration != "":
      declaration = "\"" + declaration + "\""
      embed.set_author(name = declaration, icon_url = ctx.author.avatar_url)
    
    await ctx.send(embed=embed)


  @cog_ext.cog_slash(name = "coinflip", description = "Flips a coin.", guild_ids = guild_ids)
  async def flip(self, ctx):
    rand = randint(1, 101)
    if rand == 1:
      result = "its side"
    elif rand >= 51:
      result = "tails"
    else:
      result = "heads"  
    embed = discord.Embed(description="{} flipped a coin and it landed on **{}**!".format(ctx.author.mention, result), color = ctx.author.color)
    await ctx.send(embed = embed)


  def drop_cg_loot(self, dropped_so_far, key, drop_rate):
    if randint(1, drop_rate) == 1:
      dropped_so_far[key] = dropped_so_far[key] + 1


  def calculate_dryness(self, run_count):
    dryness = pow(.9975, run_count)
    return "You had a **{:.4%}** chance of getting no drops.\nYou had a **{:.4%}** chance of getting at least one drop.".format(dryness, 1-dryness)


  def run_corrupted_gauntlet(self, user, dropped_so_far, run_count):
    dropped_so_far["crystal_shard"] = dropped_so_far["crystal_shard"] + 1 * randint(5, 9)
    self.drop_cg_loot(dropped_so_far, "crystal_armor_seed", 50)
    self.drop_cg_loot(dropped_so_far, "crystal_weapon_seed", 50)
    self.drop_cg_loot(dropped_so_far, "enhanced_crystal_weapon_seed", 400)
    self.drop_cg_loot(dropped_so_far, "younllef", 800)

    embed = discord.Embed(title = "The Corrupted Gauntlet", color = user.color)
    embed.set_author(name = "{}".format(user.name), icon_url = user.avatar_url)

    drops = []
    drops.append("{}**:** {:,}".format(Drops.CRYSTAL_SHARD.value, dropped_so_far["crystal_shard"]))
    drops.append("{}**:** {:,}".format(Drops.CRYSTAL_ARMOR_SEED.value, dropped_so_far["crystal_armor_seed"]))
    drops.append("{}**:** {:,}".format(Drops.CRYSTAL_WEAPON_SEED.value, dropped_so_far["crystal_weapon_seed"]))
    drops.append("{}**:** {:,}".format(Drops.ENHANCED_CRYSTAL_WEAPON_SEED.value, dropped_so_far["enhanced_crystal_weapon_seed"]))
    drops.append("{}**:** {:,}".format(Drops.YOUNLLEF.value, dropped_so_far["younllef"]))

    embed.add_field(name = "**Your drops:**", value = "\n".join(drops), inline = False)
    embed.add_field(name = "**Your Saeldor Dryness Score:**", value = self.calculate_dryness(run_count), inline = False)
    embed.set_thumbnail(url = "https://oldschool.runescape.wiki/images/6/6e/The_Corrupted_Gauntlet.png?e621e")
    embed.set_footer(text = "Your Corrupted Gauntlet completion count is: {:,}".format(run_count))

    return embed


  @cog_ext.cog_slash(name = "cg", description = "Run the Corrupted Gauntlet!", guild_ids = guild_ids)
  async def corrupted_gauntlet(self, ctx):
    await ctx.defer()
    run_count = 1
    dropped_so_far = {
      "crystal_shard": 0,
      "crystal_armor_seed": 0,
      "crystal_weapon_seed": 0,
      "enhanced_crystal_weapon_seed": 0,
      "younllef": 0
    }

    embed = self.run_corrupted_gauntlet(ctx.author, dropped_so_far, run_count)
    buttons = [
      manage_components.create_button(
        style = ButtonStyle.green, 
        label = "1", 
        emoji = "🔁",
        custom_id = "1"),
      manage_components.create_button(
        style = ButtonStyle.green,
        label = "10",
        emoji = "🔁",
        custom_id = "10"),
      manage_components.create_button(
        style = ButtonStyle.green,
        label = "100",
        emoji = "🔁",
        custom_id = "100")]
    action_row = manage_components.create_actionrow(*buttons)

    await ctx.send(embed = embed, components = [action_row])

    while True:
      button_ctx: ComponentContext = await wait_for_component(self.bot, components = action_row)
      for i in range(int(button_ctx.component_id)):
        run_count += 1
        embed = self.run_corrupted_gauntlet(ctx.author, dropped_so_far, run_count)
      await button_ctx.edit_origin(embed = embed)

def setup(bot):
  bot.add_cog(Random(bot))