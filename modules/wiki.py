import discord
from discord.ext import commands
from builtins import bot
from bs4 import BeautifulSoup
from flask import Flask
from titlecase import titlecase
from enum import Enum
import requests
import aiohttp
import functools

class Value(Enum):
  name = 1

class Wiki(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.replace = {
      "weapon type": "Type",
      "armor weight class": "Weight"
    }

  # grabs the first image found on the page -- this is usually the thumbnail
  def fetchThumbnail(self, url):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    links = []
    link = soup.find('img')
    imgSrc = link.get('src')
    links.append(imgSrc)
    thumb = links[0]
    return "http://wiki.dfo.world" + thumb;

  # converts the wikitext string into a nicely formatted dict
  def turn_into_dict(self, item):
    text = item["wikitext"]["*"].split("\n| ")
    attributes = {}
    for item in text:
      if "=" in item:
        kv = item.split(" = ")
        if len(kv) >= 2:
          attributes[kv[0]] = kv[1].split("==")[0].replace("\n\n", "\n").replace("}}","")
    return attributes

  @commands.command(aliases = ["dfo", "ndfo"], description = "Pulls a page from the DFO World Wiki")
  async def dfopedia(self, ctx, *, search_terms: str = None):
    if search_terms is None:
      await ctx.send(embed = discord.Embed(title = "", description = "Try searching a page with `{}dfopedia <search_term>`, {}.".format(ctx.prefix, ctx.author.mention)))
      return
    search_terms = titlecase(search_terms)
    term = search_terms.replace(" ", "%20")
    url = "http://wiki.dfo.world/api.php?action=parse&prop=wikitext&page={}&redirects&format=json".format(titlecase(term.replace(" ","%20")))
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          parse = await response.json()
    except Exception as error:
      await ctx.send(embed = discord.Embed(title = "", description = "Request failed: {}".format(error)))
      return
    await ctx.send(embed = self.parse_equipment(ctx, parse["parse"]))

  def parse_equipment(self, ctx, item_dict):
    item = self.turn_into_dict(item_dict)
    url = "http://wiki.dfo.world/view/{}".format(item_dict["title"].replace(" ", "_"))

    # getting basic item information
    level = "Level {} ".format(item["level"]) if "level" in item else ""
    slot = item["slot"] if "slot" in item else ""
    embed = discord.Embed(
      title = titlecase("**{}{} {}**".format(level, item["rarity"], slot)),
      description =
        self.exists_to_str(item, "weapon type") +
        self.exists_to_str(item, "armor weight class") +
        self.exists_to_str(item, "item type") +
        titlecase(self.exists_to_str(item, "class").replace(",", ", ")) +
        self.exists_to_str(item, "binding") +
        self.exists_to_str(item, "set"),
      color = ctx.author.color)

    # getting item's name
    embed.set_author(
      name = item_dict["title"],
      url = url,
      icon_url = "{}".format(self.fetchThumbnail(url)))

    info = ""
    # getting weapon information
    for param in ["weapon physical attack", "weapon magical attack", "independent attack"]:
      info += self.exists_to_str(item, param)
    if info:
      embed.add_field(name = "**Attack:**", value = info)
      info = ""

    # getting armor information
    for param in ["equipment physical defense", "equipment magical defense"]:
      info += self.exists_to_str(item, param)
    if info:
      embed.add_field(name = "**Defense:**", value = info, inline = False)
      info = ""

    # getting stat boost information
    for param in ["exorcism", "strength", "intelligence", "vitality", "spirit"]:
      info += self.exists_to_str(item, param, plus = True)
    for param in ["physical critical chance", "magical critical chance", "attack speed", "movement speed", "casting speed", "hit rate"]:
      info += self.exists_to_str(item, param, plus = True, percent = True)
    if info:
      embed.add_field(name = "**Stat Bonuses:**", value = info, inline = False)
      info = ""

    # getting elemental boost information
    info += self.exists_to_str(item, "inflict element")
    for param in ["all elemental damage", "fire damage", "water damage", "light damage", "shadow damage"]:
      info += self.exists_to_str(item, param)
    if info:
      embed.add_field(name = "**Elemental Stats:**", value = info, inline = False)
      info = ""

    # getting skill boost information
    info = self.skill_boost_to_str(item)
    if info:
      embed.add_field(name = "**Skill Bonuses:**", value = info, inline = False)
      info = ""

    # getting description
    info = self.format_desc(item, "description")
    if info:
      embed.add_field(name = "**Description**", value = info, inline = False)
      info = ""

    # getting flavor text
    info = self.format_desc(item, "flavor text")
    if info:
      embed.add_field(name = "**Flavor Text**", value = "_{}_".format(info), inline = False)

    embed.add_field(name = "\u3164", value = "Information provided by the DFO World Wiki\nRequested by {}".format(ctx.author.mention))

    embed.set_footer(text = "Page ID: {}".format(item_dict["pageid"]))
    return embed

  # checks if a key in the provided item dict appears
  #      return: if key exists, returns string data -- otherwise returns nothing
  #        dict: provided dictionary
  #         key: key to be checked
  def exists_to_str(self, dict, key, *, plus: bool = False, percent: bool = False):
    output = ""
    if key in dict and dict[key]:
      if key == "set":
        output = "**Set:** [{}](http://wiki.dfo.world/view/{})".format(dict[key], dict[key].replace(" ", "_"))
      else:
        output = "**{}:** {}{}{}\n".format(self.replace[key] if key in self.replace else titlecase(key), "+" if plus and not dict[key].startswith("-") else "", titlecase(dict[key]), "%" if percent else "")
      emoji = discord.utils.get(self.bot.emojis, name = key.replace(" ", ""))
      if emoji is None:
        emoji = discord.utils.get(self.bot.emojis, name = "null")
      output = "{}".format(emoji) + output
      output = "\u3164" + output
    return output

  # interprets skill boost information into a readable string
  def skill_boost_to_str(self, dict):
    output = ""
    emoji = discord.utils.get(self.bot.emojis, name = "null")
    if "all skill bonus" in dict:
      info = dict["all skill bonus"]
      info = info.split(",")
      output += "\u3164{}All Level {} - {} Skills Lv. +{} (Special Skills excluded)".format(emoji, info[1], info[2], info[3])
    if "single skill bonus" in dict:
      info = dict["single skill bonus"]
      info = info.replace("\n", "")
      info = info.split(";")
      for skill in info:
        parsed_skill = skill.split(",")
        output += "\u3164{}{} [{}](http://wiki.dfo.world/view/{}) Skill Lv. +{}\n".format(emoji, parsed_skill[0], parsed_skill[1][1:], parsed_skill[1][1:].replace(" ", "_"), parsed_skill[2][1:])
    return output

  # interprets description and flavor text into a readable string
  def format_desc(self, dict, param):
    output = ""
    if param == "description" and param in dict:
      output = self.undo_wikitext(dict["description"])
    if param == "flavor text" and param in dict:
      output = self.undo_wikitext(dict["flavor text"])
    while output.startswith("\n"):
      output = output[1:]
    while output.endswith("\n"):
      output = output[:-2]
    return output

  # removes/adapts wiki text markdown
  def undo_wikitext(self, text):
    return text.replace("<br>", "\n").replace("\n\n", "\n").replace("{{IconLink|", "").replace("}}", "").replace("[", "").replace("]", "").replace("'", "")

def setup(bot):
  bot.add_cog(Wiki(bot))