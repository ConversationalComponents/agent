import os
import sys
import importlib
import logging

from aiogram import Bot, Dispatcher, executor, types

from agt.server import AgentSessionsManager

API_TOKEN = os.environ["TELEGRAM_TOKEN"]

# Configure logging
logging.basicConfig(filename="agt-telegram.log", level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


_, entry_path, *args = sys.argv

entry_package_name, entry_name = entry_path.rsplit(".", 1)

entry_package = importlib.import_module(entry_package_name)
entry = getattr(entry_package, entry_name)

sess_mgr = AgentSessionsManager()


class OutputCallback:
    def __init__(self, chat_id) -> None:
        self.chat_id = chat_id

    async def __call__(self, text, image_url=None, *args, **kwargs):
        await bot.send_message(self.chat_id, text)


@dp.message_handler()
async def on_message(message: types.Message):

    session_id = message.chat.id

    output_callback = OutputCallback(message.chat.id)

    sc = sess_mgr.get_session(session_id, entry, output_callback)

    sc.conv_state.memory["user_id"] = message.chat.id

    await sc.conv_state.put_user_input(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
