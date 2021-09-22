# Future
from __future__ import annotations

# Packages
import aiohttp.web
import discord

# My stuff
from core import config


ZWSP = "\u200b"
NL = "\n"

PERMISSIONS = discord.Permissions(
    read_messages=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    add_reactions=True,
    external_emojis=True,
)

INVITE_LINK = discord.utils.oauth_url(
    client_id=config.CLIENT_ID,
    permissions=PERMISSIONS,
    scopes=["bot", "applications.commands"],
)
