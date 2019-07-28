import random
import re
import json
import importlib.resources

import puppet

from .preconfigured import basic_nlu_interpreter
from . import data_files

eliza_data = json.loads(importlib.resources.read_text(data_files, "eliza.json"))

eliza_patterns = eliza_data.get("patterns")
eliza_refelections = eliza_data.get("reflections")


def reflect_input(user_input):
    updated_input = user_input
    for search_string, replacement in eliza_refelections.items():
        updated_input = re.sub(f"(^|\s){search_string}(\s|$)",
                               f"\g<1>###{replacement}###\g<2>",
                               updated_input,
                               0,
                               re.IGNORECASE)
    updated_input = updated_input.replace("###", "")
    return updated_input

def get_eliza_response(user_input):
    for pattern, response_alternates in eliza_patterns:
        m = re.match(pattern, user_input, re.IGNORECASE)
        if m:
            selected_response = random.choice(response_alternates)
            for ig, g in enumerate(m.groups()):
                reflected_group = reflect_input(g)
                selected_response = selected_response.replace(f"%{ig+1}",
                                                              reflected_group)
            return selected_response

def eliza_main(state: puppet.ConversationState):
    while True:
        last_line = state.get_last_user_input().text
        yield get_eliza_response(last_line)


def interpret_from_state(state, hypotheses):
    last_line = state.get_last_user_input().text
    return basic_nlu_interpreter.interpret(last_line, hypotheses)

def welcome_line(state: puppet.ConversationState):
    o = interpret_from_state(state, ["greet", "whatup"])
    if "greet" in o and "whatup" in o:
        yield "Hi, I'm fine, How are you feeling today?"
    elif "greet" in o:
        yield "Hi, How are you feeling today?"
    else:
        yield "How are you feeling today?"
    o = interpret_from_state(state, ["user_feels_fine", "user_feels_not_fine"])
    if "user_feels_fine" in o:
        yield "That's great! I'm happy to hear it 😀 So, what are you up to today?"
    elif "user_feels_not_fine" in o:
        yield "Aw, that's too bad 😢  How can I cheer you up?"

def eliza(state):
    yield from welcome_line(state)
    yield from eliza_main(state)

