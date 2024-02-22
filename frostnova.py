from os.path import dirname, basename, isfile
import sys
import os
import importlib
import inspect
import discord
import time
from discord import app_commands
from discord.ext import commands

from typing import List, Optional
import Paginator
import boto3
import base64
import asyncio

from cogs.utils.keywords import Keyword as ky


prefix = "░▒▓ (\\_/) " 

class FrostNova(commands.Bot):
    def __init__(self) -> None:
        self.start_time = time.time()
        self.api_keys = self.get_secrets_from_aws()
        command_prefix = "fn$"
        intents = discord.Intents.all()
        intents.typing = False
        intents.presences = False
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix = command_prefix, 
            intents = intents,
            owner_id = 94236862280892416,
            status = discord.Status.online,
            activity = discord.Game(name = "明日方舟", type = discord.ActivityType.competing)
        )


    def get_start_time(self):
        return self.start_time


    def get_api_key(self, key_name):
        return self.api_keys.get(key_name, None)


    def create_error_response(self, message: str = None, error: Exception = None):
        description = message if message else f"**{type(error).__name__}:** {error}"
        embed = discord.Embed(title = "", description = f"{ky.ERROR.value} {description}")
        return embed


    def create_paginated_embed(self):
        previous_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = ky.LEFT.value)
        next_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = ky.RIGHT.value)
        return Paginator.Simple(PreviousButton = previous_button, NextButton = next_button)


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


    def get_secrets_from_aws(self):
        secret_names = ["FrostNova", "DFO-APIKey"]
        region_name = "us-east-1"
        api_keys = {}

        # create secrets manager client
        session = boto3.session.Session()
        client = session.client(service_name = 'secretsmanager', region_name = region_name)

        try:
            for secret_name in secret_names:
                get_secret_value_response = client.get_secret_value(SecretId = secret_name)
                if 'SecretString' in get_secret_value_response:
                    # api_keys[secret_name] = get_secret_value_response['SecretString'][18:-2]
                    api_keys[secret_name] = get_secret_value_response['SecretString']
                else:
                    # api_keys[secret_name] = base64.b64decode(get_secret_value_response['SecretBinary'])[18:-2]
                    api_keys[secret_name] = base64.b64decode(get_secret_value_response['SecretBinary'])
                print(f"Successfully retrieved AWS secret for {secret_name}.")
        except ClientError as e:
            error_code = e.repsonse['Error']['Code']
            error_https_code = e.response['ResponseMetadata']['HTTPStatusCode']
            error_msg = e.response['Error']['Message']
            print("Error Code {} ({}): {}".format(error_code, error_https_code, error_msg))
            raise e
        return api_keys


bot = FrostNova()
bot.run(bot.get_api_key("FrostNova")[18:-2])