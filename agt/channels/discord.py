import os
import sys
import importlib
import logging

import discord

from discord.channel import DMChannel
from discord import Message, Embed

from ..server import AgentSessionsManager

logging.basicConfig(filename="agt-discord.log", level=logging.DEBUG)

DISCORD_KEY = os.environ.get("DISCORD_KEY", "")

_, entry_path, *args = sys.argv

entry_package_name, entry_name = entry_path.rsplit(".", 1)

entry_package = importlib.import_module(entry_package_name)
entry = getattr(entry_package, entry_name)

sess_mgr = AgentSessionsManager()

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


class OutputCallback:
    def __init__(self, channel) -> None:
        self.channel = channel

    async def __call__(self, text, image_url=None, *args, **kwargs):
        embed = None
        if image_url:
            embed = Embed().set_image(url=image_url)
        await self.channel.send(text, embed=embed)


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

    output_callback = OutputCallback(target_channel)

    sc = sess_mgr.get_session(session_id, entry, output_callback)

    sc.conv_state.memory["user_id"] = "#".join(
        (message.author.name, message.author.discriminator)
    )

    await sc.conv_state.put_user_input(message.content)


client.run(DISCORD_KEY)
