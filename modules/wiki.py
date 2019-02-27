import discord
from discord.ext import commands
from builtins import bot

from bs4 import BeautifulSoup
from flask import Flask
from titlecase import titlecase
from random import choice
import requests

# Parses wikipedia pages and pulls some information utilizing BeautifulSoup 4

def fetchThumbnail(url):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    links = []
    link = soup.find('img')
    imgSrc = link.get('src')
    links.append(imgSrc)
    thumb = links[0]
    return thumb;

@bot.command(pass_context=True, description = "Pulls a page from the DFO World Wiki.")
async def dfopedia(ctx, *, search_terms: str=None):
    '''Searches the DFO Wiki.'''

    if search_terms is None:
      # catches null-answer
      embed = discord.Embed(title ="", description = "Try asking a question with `!dfopedia <search_term>`, {}".format(ctx.message.author.mention), color = 0xe74c3c)
      await bot.say(embed = embed)
    
    else:
      # sanitizes the search term to make it URL friendly

      search_terms = titlecase(search_terms)
      term = search_terms.replace(" ", "_")
      result = "http://wiki.dfo.world/view/index.php?search={}&title=Special%3ASearch&go=GO".format(term)

      # grabs the first image on the page
      thumb = fetchThumbnail(result)

      # creates the message
      embed = discord.Embed(title = search_terms, description = "Requested by **" + ctx.message.author.mention + "**\nPowered by the **[DFO World Wiki](http://wiki.dfo.world/view/Main_Page)**.", url=result, color=makeColor())
      embed.set_thumbnail(url = "http://wiki.dfo.world" + thumb)
      
      try:
        await bot.say(embed = embed)

      except:
        # exception is raised if for some reason the page cannot be accessed
        error = discord.Embed(title = "", description = "If Becky appears to the right, then the requested page does not exist. If she does not, then the [DFO World Wiki](http://wiki.dfo.world/view/Main_Page) may be offline. Either double-check your spelling, or try again later.", color=0xf19630)
        error.set_author(name = "Whoops! I couldn't find {}!".format(search_terms))
        error.set_thumbnail(url = "http://wiki.dfo.world/images/0/0a/Beckyportrait.png")
        await bot.say(embed = error)