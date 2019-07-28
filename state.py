""" conversation state definition """
import typing as ta
from dataclasses import dataclass, field

import marshmallow

@dataclass
class Message:
    text: str
    speaker: str

@dataclass
class ConversationState:
    log: ta.List[Message] = field(default_factory=list)

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

    @marshmallow.post_load
    def make_conv_state(self, data, **kwargs):
        return ConversationState(**data)
