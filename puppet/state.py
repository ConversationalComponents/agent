""" conversation state definition """
import typing as ta
import uuid

from asyncio import Queue

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
    def __init__(self, output_callback):
        self.output_callback = output_callback
        self.session_id = generate_session_id()
        self.log = []
        self.out_of_context_handlers = []
        self.inputs_queue = None
    
    async def say(self, text):
        self.log.append(BotEntry(text))
        await self.output_callback(text)
    
    async def put_user_input(self, user_input: str):
        if not self.inputs_queue:
            self.inputs_queue = Queue()

        await self.inputs_queue.put(user_input)

    async def user_input(self):
        if not self.inputs_queue:
            self.inputs_queue = Queue()

        user_input = await self.inputs_queue.get()
        self.log.append(UserEntry(user_input))
        return user_input
    
    def last_user_input(self):
        last_user_input = next(filter(lambda e: isinstance(e, UserEntry), reversed(self.log)), None)
        if last_user_input:
            return last_user_input.text
    
    def set_out_of_context_handler(self, handler):
        self.out_of_context_handlers.append(handler)
    
    def pop_out_of_context_handler(self):
        self.out_of_context_handlers.pop()

    async def out_of_context(self, *args, **kwargs):
        if len(self.out_of_context_handlers) > 0:
            await self.out_of_context_handlers[-1](self, *args, **kwargs)

class OutOfContext(object):
    def __init__(self, state, handler):
        self.state = state
        self.state.set_out_of_context_handler(handler)
    def __enter__(self):
        return self.state
    def __exit__(self, type, value, traceback):
        self.state.pop_out_of_context_handler()

class TerminationState(object):
    def __init__(self, success=True):
        self.success = success
        self.failure = not success