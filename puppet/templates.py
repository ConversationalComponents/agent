async def pick_first_match(user_input, intent_map, default=None):
    for intent, (callback, *args) in intent_map.items():
        if intent(user_input):
            return await callback(*args)
    if default:
        func, *args = default
        return await func(*args)