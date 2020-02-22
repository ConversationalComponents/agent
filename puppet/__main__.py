import asyncio
import sys
import importlib

from .shell import bot_runner

entry_path = sys.argv[1]

entry_package_name, entry_name = entry_path.rsplit(".", 1)

entry_package = importlib.import_module(entry_package_name)
entry = getattr(entry_package, entry_name)

asyncio.run(bot_runner(entry))