import asyncio
import puppet

from puppet import ConversationState
from puppet.helpers import pick_first_match

class ExampleIntent:
    def __init__(self, example):
        self.example = example
    def __call__(self, user_input):
        return self.example in user_input
intent_hi = ExampleIntent("hi")
intent_no = ExampleIntent("no")
intent_yes = ExampleIntent("yes")

async def sample_bot(state):
    await state.say("Welcome")
    user_input = await state.user_input()
    await pick_first_match(
        user_input,
        {
            intent_hi: (state.say, "hello back, how can I help")
        },
        (state.say, "How can I help?")
    )
    await lobby(state)

async def lobby(state):
    while True:
        user_input = await state.user_input()
        await pick_first_match(
            user_input,
            {
                (lambda x: "drink" in x): (drink_comp, state),
                (lambda x: "pizza" in x): (pizza_comp, state)
            },
            (state.say, "I can only help you order a pizza or a drink")
        )
    
async def pizza_comp(state):
    await state.say("what kind of pizza do you want?")
    user_input = await state.user_input()
    await pick_first_match(
        user_input,
        {
            (lambda x: "regular" in x): (state.say, "ok one regular"),
            (lambda x: "pan" in x): (state.say, "ok one pan"),
        },
        (state.say, "I don't have that")
    )

async def drink_comp(state):
    await state.say("what drink do you want?")
    user_input = await state.user_input()
    await pick_first_match(
        user_input,
        {
            (lambda x: "espresso" in x): (state.say, "ok one espresso"),
        },
        (state.say, "I don't have that")
    )
    

async def get_first_name(state: ConversationState, user_input):
    if not user_input:
        user_input = await state.user_input()
    if "chen" in user_input:
        return
    await state.say("will you please tell me your first name?")
    
async def get_last_name(state: ConversationState, user_input):
    if not user_input:
        user_input = await state.user_input()
    if "buskilla" in user_input:
        return
    await state.say("will you please tell me your last name?")
    
async def namer(state: ConversationState):
    user_input = await state.user_input()
    if "chen" in user_input and "buskilla" in user_input:
        return
    elif "chen" in user_input:
        return await get_last_name(state, user_input)
    elif "buskilla" in user_input:
        return await get_first_name(state, user_input)
    else:
        await state.say("will you please tell me your name?")
        user_input = await state.user_input()
        await get_first_name(state, user_input)
        await get_last_name(state, user_input)
        return

async def greet(state: ConversationState):
    await state.say("Welcome")
    user_input = await state.user_input()
    await state.out_of_context()
    if intent_hi(user_input):
        await state.say("Hello, How can I help?")
    else:
        await state.say("How can I help?")
    return "component_done"

s = puppet.ConversationState(print, input)
asyncio.run(sample_bot(s))