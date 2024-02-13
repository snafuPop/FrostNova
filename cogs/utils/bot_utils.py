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


class EmojiMeta(type):
    def __mul__(cls, n):
        return str(cls) * n


class Emojis(metaclass=EmojiMeta):  # Store emoji that need to be used in output here and allow other modules to import them to promote consistency
    LEFT = "<:left:1011270488326144020>"
    RIGHT = "<:right:1011270489206952036>"
    SUCCESS = ":white_check_mark:"
    YES = "<:yes:603662870567190597>"
    NO = "<:no:603662870365995019>"
    ERROR = ":no_entry:"
    LOAD = ":record_button:"
    UNLOAD = ":eject:"
    RELOAD = ":repeat:"
    BULLET = "▪️"
    BOOST = "<:boost:907765841771257928>"
    CURRENCY = "<:lmd:1205576503614504980>"
    NAMETAG = "<:nametag:1009939862180352000>"
    FAME = "<:fame:1138589542098686085>"
    EMPTY = "<:blank:1205612541691035689>"


def create_error_response(message: str = None, error: Exception = None):
    """Generates and returns an embedded error message, whether the error is triggered by user-input or by an exception."""
    description = message if message else f"**{type(error).__name__}:** {error}"
    embed = discord.Embed(title = "", description = f"{Emojis.ERROR} {description}")
    return embed


def create_paginated_embed():
    """Creates a Paginated object that will allow users to navigate between multiple embedded messages."""
    previous_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = Emojis.LEFT)
    next_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = Emojis.RIGHT)
    return Paginator.Simple(PreviousButton = previous_button, NextButton = next_button)
