""" conversation state definition """
import typing as ta
import uuid

def generate_session_id():
    return str(uuid.uuid4())

class ConversationState(object):
    def __init__(self, output_callback, input_callback):
        self.input_callback = input_callback
        self.output_callback = output_callback
        self.session_id = generate_session_id()
    
    async def say(self, text):
        self.output_callback(text)
    
    async def user_input(self):
        return self.input_callback()
    
    async def out_of_context(self):
        pass

class TerminationState(object):
    def __init__(self, success=True):
        self.success = success
        self.failure = not success