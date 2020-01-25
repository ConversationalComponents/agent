""" conversation state definition """
import typing as ta
import uuid

def generate_session_id():
    return str(uuid.uuid4())

class Entry:
    def __init__(self, text: str):
        self.text = text

class BotEntry(Entry):
    pass

class UserEntry(Entry):
    pass

class ConversationState(object):
    def __init__(self, output_callback, input_callback):
        self.input_callback = input_callback
        self.output_callback = output_callback
        self.session_id = generate_session_id()
        self.log = []
    
    async def say(self, text):
        self.log.append(BotEntry(text))
        self.output_callback(text)
    
    async def user_input(self):
        user_input = self.input_callback()
        self.log.append(UserEntry(user_input))
        return user_input
    
    def last_user_input(self):
        last_user_input = next(filter(lambda e: isinstance(e, UserEntry), reversed(self.log)), None)
        if last_user_input:
            return last_user_input.text
    
    async def out_of_context(self):
        pass

class TerminationState(object):
    def __init__(self, success=True):
        self.success = success
        self.failure = not success

def generate_console_state():
    console_input = lambda: input("User: ")
    console_output = lambda text: print(f"Bot: {text}")
    return ConversationState(console_output, console_input)