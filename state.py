""" conversation state definition """
import typing as ta
import uuid
from dataclasses import dataclass, field

import marshmallow

def generate_session_id():
    return str(uuid.uuid4())

@dataclass
class Message:
    text: str
    speaker: str

@dataclass
class ConversationState:
    log: ta.List[Message] = field(default_factory=list)
    session_id: str = field(default_factory=generate_session_id)

    def log_message(self, speaker: str, text: str) -> None:
        self.log.append(Message(speaker=speaker, text=text))

    def get_last_user_input(self) -> Message:
        for msg in reversed(self.log):
            if msg.speaker == "user":
                return msg
        return None

class MessageSchema(marshmallow.Schema):
    text = marshmallow.fields.String()
    speaker = marshmallow.fields.String()

    @marshmallow.post_load
    def make_exchange(self, data, **kwargs):
        return Message(**data)

class ConversationStateSchema(marshmallow.Schema):
    log = marshmallow.fields.Nested(MessageSchema, many=True)
    session_id = marshmallow.fields.String()

    @marshmallow.post_load
    def make_conv_state(self, data, **kwargs):
        return ConversationState(**data)
