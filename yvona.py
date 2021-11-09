from os.path import dirname, basename, isfile
import sys
import glob
import os
import builtins
import importlib
import inspect
import discord
from discord import Client, Intents, Embed
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord.ext.commands import Bot
import boto3
import base64

def get_secret_from_aws():
  secret_name = "yvona_token"
  region_name = "us-east-1"

  # create secrets manager client
  session = boto3.session.Session()
  client = session.client(service_name = 'secretsmanager', region_name = region_name)

  try:
    get_secret_value_response = client.get_secret_value(SecretId = secret_name)
  except ClientError as e:
    error_code = e.repsonse['Error']['Code']
    error_https_code = e.response['ResponseMetadata']['HTTPStatusCode']
    error_msg = e.response['Error']['Message']
    print("Error Code {} ({}): {}".format(error_code, error_https_code, error_msg))
    raise e

  else:
    # decrypts secret using the associated KMS CMK.
    # depending on whether the secret is a string or binary, one of these fields will be populated.
    return get_secret_value_response['SecretString'] if 'SecretString' in get_secret_value_response else base64.b64decode(get_secret_value_response['SecretBinary'])


def load_intents():
  # load intents
  intents = Intents.default()
  intents.members = True
  intents.guilds = True
  intents.emojis = True
  intents.messages = True
  intents.guild_messages = True
  intents.dm_messages = True
  intents.reactions = True
  intents.guild_reactions = True
  return intents


def load_modules():
  successful_imports = 0
  total_imports = 0

  modules_path = os.path.join(os.path.dirname(__file__), 'modules/')
  print("\n")
  for file in os.listdir(modules_path):
    filename = os.fsdecode(file)
    if filename != "__init__.py" and filename.endswith(".py"):
      total_imports += 1
      try:
        bot.load_extension("modules." + filename[:-3])
        print("{} was loaded successfully!".format(filename))
        successful_imports += 1
      except Exception as e:
        print("{} could not be loaded ({}: {})".format(filename, type(e).__name__, e))
  print("\n{}/{} modules loaded".format(successful_imports, total_imports), flush = True)


# ------------------------------------------------------------


token = get_secret_from_aws().split(":")[1][1:-2]
bot = Bot(command_prefix = "yv ", self_bot = True, help_command = None, intents = load_intents())
slash = SlashCommand(bot, sync_commands = True)
guild_ids = [482725089217871893] # test server ID for testing un-synced commands privately
builtins.bot = bot
builtins.guild_ids = guild_ids
load_modules()

@bot.event
async def on_ready():
  # runs when the bot is fully functional
  print("Logged in as {} <{}>".format(bot.user.name, bot.user.id), flush = True)
  print("Running {}".format(discord.__version__), flush = True)
  print("--------------------------------------------------------", flush = True)

bot.run(token)
