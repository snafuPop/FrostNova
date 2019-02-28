import discord
from discord.ext import commands
from builtins import bot

@bot.command(description = "Prints markdown text utilized by Discord")
async def syntax():
  embed = discord.Embed(title = "Markdown utilized by Discord:")
  embed.add_field(name = "*italics*", value = "`*italics*` or `_italics_`")
  embed.add_field(name = "**bold**", value = "`**bold**`", inline = True)
  embed.add_field(name = "__underline__", value = "`__underline__`", inline = True)
  embed.add_field(name = "~~strikethrough~~", value = "`~~strikethrough~~`", inline = True)
  embed.add_field(name = "||spoiler||", value = "`||spoiler||`", inline = True)

  embed.add_field(name = "`single-line code`", value = "surround text with `")
  embed.add_field(name = "```multi-line code```", value = "surround text with 3 `'s. Define a language by typing the name of the language after the three backticks", inline = True)

  await bot.say(embed = embed)

@bot.command(pass_context = True, description = "Gives information about a user")
async def scan(ctx, *, user: discord.Member = None):
  # prints information about a user

  # grabbing the user's username (defaults to the author if a user was not specified)

  try:
    if user is None:
      user = ctx.message.author
  except Exception as e:
    embed = discord.Embed(title = "", description = "It doesn't seem like {} is a member of this server. Maybe try mentioning them instead?")
  else:
    # grabs all of the user's roles (except the default role) and converts it to a string
    roles = []
    for role in user.roles:
      if role.name != "@everyone":
        roles.append(role.name)
    if roles:
      roles = ", ".join(roles)
    else:
      roles = "None"

    if user.nick is not None:
      nick = '(' + user.nick + ')'
    else:
      nick = ""

    # sets user information as the title
    embed = discord.Embed(title = "__**{}**__ {}".format(str(user), nick), description = "**roles:** {}".format(roles), color = user.color)

    # sets the user's avatar as the image (if they have one)
    if user.avatar_url:
      embed.set_thumbnail(url = user.avatar_url)

    # displays account age
    embed.add_field(name = "Discord user since:", value = user.created_at.strftime("%d %b %Y"), inline = True)
    embed.add_field(name = "Joined server at:", value = user.joined_at.strftime("%d %b %Y"), inline = True)

    if user.game is not None:
      embed.set_footer(text = "Currently playing {}".format(user.game))

  await bot.say(embed = embed)

@bot.command(pass_context = True, description = "Gives information about the current server")
async def server(ctx):
  server = ctx.message.server
  embed = discord.Embed(title = "__**{}**__".format(str(server.name)), description = "Based in {}".format(str(server.region)))
  embed.add_field(name = "Number of members:", value = str(len(server.members)), inline = True)
  embed.add_field(name = "Owner", value = str(server.owner), inline = True)