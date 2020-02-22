import asyncio
from .state import ConversationState
from aioconsole import ainput

async def input_loop(s):
    while True:
        await s.put_user_input(await ainput())

async def console_output(text):
    print(f"Bot: {text}")

async def bot_runner(bot):
    s = ConversationState(console_output)
    await asyncio.gather(
        input_loop(s), 
        bot(s))