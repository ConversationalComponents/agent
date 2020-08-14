import typing
from agt.nlu.word_regex import Intent, Pattern, WILDCARD, AnyWords


yes_intent = Intent(
    Pattern(WILDCARD, ("yes", "yup", "sure", "yep", "yeah", "yea"), WILDCARD),
    Pattern("y"),
)

no_intent = Intent(
    Pattern(WILDCARD, ("no", "nope", "nop", "never"), WILDCARD), Pattern("n")
)


async def say_component(state, text):
    await state.say(text)


def pack_followup_action(state, followup_action):
    if isinstance(followup_action, typing.Awaitable):
        return followup_action
    elif isinstance(followup_action, str):
        return say_component(state, followup_action)

    raise ValueError("Invalid follow-up action")


def followup(intent, followup_action):
    return intent, followup_action


def keywords(keywords_list, followup_action):
    return Intent(Pattern(WILDCARD, keywords_list, WILDCARD)), followup_action


def followups(*followups_intent_actions, yes=None, no=None, default=None):
    async def followup_comp(state, user_input=None):
        if not user_input:
            user_input = await state.user_input()

        followup_actions = []
        if yes:
            followup_actions.append((yes_intent, yes))
        if no:
            followup_actions.append((no_intent, no))

        followup_actions.extend(followups_intent_actions)

        for intent, followup_action in followup_actions:
            if intent(user_input):
                return await pack_followup_action(state, followup_action)

        if default:
            return await pack_followup_action(state, default)

    return followup_comp


async def pick_first_match(user_input, intent_map, default=None):
    for intent, (callback, *args) in intent_map.items():
        if intent(user_input):
            return await callback(*args)
    if default:
        func, *args = default
        return await func(*args)
