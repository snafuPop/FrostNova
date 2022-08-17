from os.path import dirname, basename, isfile
import sys
import os
import importlib
import inspect
import discord
from discord import app_commands
from discord.ext import commands

from typing import List, Optional
import boto3
import base64
import asyncio
import Paginator

from cogs.utils.keywords import Keyword as ky


prefix = "░▒▓ (\\_/) " 

class FrostNova(commands.Bot):
  def __init__(self) -> None:
      command_prefix = "fn$",
      intents = discord.Intents.default()
      intents.members = True
      intents.guilds = True
      intents.emojis = True
      intents.messages = True
      intents.guild_messages = True
      intents.dm_messages = True
      intents.reactions = True
      intents.guild_reactions = True
      super().__init__(command_prefix = command_prefix, intents = intents)


  def create_error_response(self, message: str = None, error: Exception = None):
    description = message if message else f"**{type(error).__name__}:** {error}"
    embed = discord.Embed(title = "", description = f"{ky.ERROR.value} {description}")
    return embed


  async def on_ready(self):
    print(f"Logged in as {bot.user.name} <{bot.user.id}>")
    print(f"Running {discord.__version__}")
    print("--------------------------------------------------------")


  async def setup_hook(self):
    successful_imports = 0
    total_imports = 0

    cogs = os.path.join(os.path.dirname(__file__), 'cogs/')
    for cog in os.listdir(cogs):
      cog_name = os.fsdecode(cog)
      if cog_name != "__init__.py" and cog_name.endswith(".py"):
        total_imports += 1
        try:
          await self.load_extension(f"cogs.{cog_name[:-3]}")
          print(f"O: {cog_name} was loaded successfully!")
          successful_imports += 1
        except Exception as error:
          print(f"X: {cog_name} could not be loaded ({type(error).__name__}: {error})")
    print(f"\n{successful_imports}/{total_imports} cog(s) loaded.")

    if successful_imports == 0:
      print("No cogs were successfully loaded, terminating.")
      sys.exit()

    guild = discord.Object(482725089217871893)
    self.tree.copy_global_to(guild = guild)
    synced = await self.tree.sync(guild = guild)
    print(f"Synced {len(synced)} commands to test guild {guild.id}.")


def get_secret_from_aws():
  secret_name = "FrostNova"
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
    value = get_secret_value_response['SecretString'] if 'SecretString' in get_secret_value_response else base64.b64decode(get_secret_value_response['SecretBinary'])
    return value[18:-2]



bot = FrostNova()
bot.run(get_secret_from_aws())