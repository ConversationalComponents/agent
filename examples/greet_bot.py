from puppet.templates import pick_first_match
from puppet import coco

class ExampleIntent:
    def __init__(self, example):
        self.example = example
    def __call__(self, user_input):
        return self.example in user_input
intent_hi = ExampleIntent("hi")
intent_no = ExampleIntent("no")
intent_yes = ExampleIntent("yes")

async def sample_bot(state):
    await state.say("Welcome to sample bot")
    user_input = await state.user_input()
    await coco(state, "namer_vp3", user_input)
    await coco(state, "register_vp3")
    await help_line(state)
    await lobby(state)

async def help_line(state):
    user_input = state.last_user_input()
    await pick_first_match(
        user_input,
        {
            intent_hi: (state.say, "hello back, how can I help")
        },
        (state.say, "How can I help?")
    )

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

if __name__ == "__main__":
    import asyncio
    from puppet import generate_console_state
    s = generate_console_state()
    asyncio.run(sample_bot(s))