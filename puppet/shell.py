import asyncio
from .state import ConversationState
from aioconsole import ainput


async def input_loop(s) -> None:
    while True:
        await s.put_user_input(await ainput())


async def console_output(text, *args, **kwargs):
    print(f"Bot: {text}")


async def bot_init(bot, *args, **kwargs) -> None:
    s = ConversationState(console_output)
    s.memory["user_id"] = "shelluser"
    await asyncio.gather(input_loop(s), bot(s, *args, **kwargs))


def bot_runner(bot, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot_init(bot, *args, **kwargs))
