import sys
import importlib

import puppet

state = puppet.ConversationState()

entry_path = sys.argv[1]

entry_package_name, entry_name = entry_path.rsplit(".", 1)

entry_package = importlib.import_module(entry_package_name)
entry = getattr(entry_package, entry_name)

entry_iter = entry(state)

while True:
    user_input = input("U: ")
    state.log_message("user", user_input)
    resp = next(entry_iter, "END")
    state.log_message("bot", resp)
    print(f"B: {resp}")
