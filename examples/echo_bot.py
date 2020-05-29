import asyncio

from puppet.shell import bot_runner


async def echo(state):
    user_input = await state.user_input()
    await state.say(user_input)


if __name__ == "__main__":
    asyncio.run(bot_runner(echo))
