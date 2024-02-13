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


def create_error_response(message: str = None, error: Exception = None):
    """Generates and returns an embedded error message, whether the error is triggered by user-input or by an exception."""
    description = message if message else f"**{type(error).__name__}:** {error}"
    embed = discord.Embed(title = "", description = f"{ky.ERROR.value} {description}")
    return embed


def create_paginated_embed():
    """Creates a Paginated object that will allow users to navigate between multiple embedded messages."""
    previous_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = ky.LEFT.value)
    next_button = discord.ui.Button(style = discord.ButtonStyle.success, emoji = ky.RIGHT.value)
    return Paginator.Simple(PreviousButton = previous_button, NextButton = next_button)
