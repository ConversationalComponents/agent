import os
import asyncio
import sys
import importlib

import discord

from discord.channel import DMChannel
from discord import Message

from .server import PuppetSessionsManager

DISCORD_KEY = os.environ.get("DISCORD_KEY", "")

_, entry_path, *args = sys.argv

entry_package_name, entry_name = entry_path.rsplit(".", 1)

entry_package = importlib.import_module(entry_package_name)
entry = getattr(entry_package, entry_name)

sess_mgr = PuppetSessionsManager()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message: Message):

    if client.user in message.mentions:
        pass
    elif message.author == client.user or not isinstance(message.channel, DMChannel):
        return

    session_id = message.author.id

    if isinstance(message.channel, DMChannel):
        target_channel = message.channel
    else:
        target_channel = message.author

    sc = sess_mgr.get_session(session_id, entry, target_channel.send)

    await sc.conv_state.put_user_input(message.content)

client.run(DISCORD_KEY)
