from typing import List, Optional
import enum
import json
import random

from pydantic import BaseModel


import coco.async_api as coco_sdk
from coco import ccml

import agt
from agt.state import OutOfContext, Outputs, ConversationState
from agt.nlu.word_regex import Intent, Pattern, WILDCARD

from coco.config_models import ActionsConfig, BlueprintConfig

available_intents = {
    "yes": Intent(
        Pattern(
            WILDCARD,
            (
                "yes",
                "yea",
                "yup",
                "sure",
                "ok",
                "of course",
                "yeah",
                "okay",
                "yep",
                "I do",
            ),
            WILDCARD,
        ),
        Pattern(("y", "totally", "naturally", "k")),
    ),
    "no": Intent(
        Pattern(
            WILDCARD,
            (
                "no",
                "nope",
                "never",
                "no way",
                "nah",
                "neh",
                "nay",
                "nop",
                "noo",
                "nooo",
            ),
            WILDCARD,
        ),
        Pattern("n"),
    ),
    "continue": Intent(
        Pattern(WILDCARD, ("yes", "yea", "yup", "sure", "ok"), WILDCARD),
        Pattern(("and", "go on")),
    ),
    "stop": Intent(
        Pattern(("stop", "bye", "this is boring")),
    ),
    "wildcard": Intent(Pattern(WILDCARD)),
}

AvailableIntents = enum.Enum(
    "AvailableIntents", zip(available_intents.keys(), available_intents.keys())
)


class OneTurnFollowup(BaseModel):
    intent_name: Optional[AvailableIntents]
    keywords: Optional[List[str]]
    followup_response: str


class OneTurnConfig(BlueprintConfig):
    oneturn_followups: List[OneTurnFollowup]
    available_intents: List[AvailableIntents] = list(AvailableIntents)


FOLLOWUP_CONFIG = json.loads(
    OneTurnConfig(
        blueprint_id="oneturn_followup",
        oneturn_followups=[
            OneTurnFollowup(intent_name=AvailableIntents.yes, followup_response="good"),
            OneTurnFollowup(
                intent_name=AvailableIntents.no, followup_response="but why?!"
            ),
            OneTurnFollowup(
                intent_name=AvailableIntents.stop, followup_response="ok bye!"
            ),
            OneTurnFollowup(keywords=["vanilla"], followup_response="good choice"),
        ],
    ).json()
)


def clean_keywords(keywords: List[str]) -> List[str]:
    return [k.strip() for k in keywords if isinstance(k, str) and len(k.strip()) > 0]


async def oneturn_followup(state: agt.ConversationState, config=FOLLOWUP_CONFIG):
    config_model: OneTurnConfig = OneTurnConfig.validate(config)
    user_input = await state.user_input()
    for fu in config_model.oneturn_followups:
        if fu.intent_name and available_intents[fu.intent_name.name](user_input):
            await state.say(fu.followup_response)
            return Outputs(control=fu.intent_name.name)
        if fu.keywords and Intent(
            Pattern(WILDCARD, clean_keywords(fu.keywords), WILDCARD)
        )(user_input):
            await state.say(fu.followup_response)
            return Outputs(control=fu.keywords[0])
    await state.out_of_context(user_input)


SAY_CONFIG = ActionsConfig(
    blueprint_id="oneturn_say", action_config={"line": ["This is a line"]}
).dict()


async def oneturn_say(state: agt.ConversationState, config=SAY_CONFIG):
    config_model: ActionsConfig = ActionsConfig.validate(config)
    await state.say(config_model.action_config["line"][0])


async def oneturn_say_v2(state: agt.ConversationState, line="This is a line", **kwargs):
    text = ccml.parse.clear_xml_tags(line)
    await state.say(text=text, ssml=line)


async def oneturn_say_v3(state: agt.ConversationState, lines=["This is a line"]):
    choosen_line = random.choice(lines)
    text = ccml.parse.clear_xml_tags(choosen_line)
    await state.say(text=text, ssml=choosen_line)


async def oneturn_followup_v2(
    state: agt.ConversationState, followups: List[OneTurnFollowup] = []
):
    user_input = await state.user_input()
    for fu_dict in followups:
        fu = OneTurnFollowup.validate(fu_dict)
        if fu.intent_name and available_intents[fu.intent_name.name](user_input):
            await state.say(fu.followup_response)
            return Outputs(control=fu.intent_name.name)
        if fu.keywords and Intent(
            Pattern(WILDCARD, clean_keywords(fu.keywords), WILDCARD)
        )(user_input):
            await state.say(fu.followup_response)
            return Outputs(control=fu.keywords[0])
    await state.out_of_context(user_input)


async def oneturn_say_followup(
    state: agt.ConversationState,
    line="This is a line",
    followups: List[OneTurnFollowup] = [],
):
    await state.say(line)
    return await oneturn_followup_v2(state, followups=followups)


async def save_to_context(state: agt.ConversationState, **params):
    state.memory.update(params)


async def aggregate_context(state: agt.ConversationState, **params):
    for k, v in params.items():
        if not isinstance(state.memory.get(k, []), list):
            state.memory[k] = [state.memory[k]]
        state.memory[k] = state.memory.get(k, []) + [v]


async def input_aggregator(state: agt.ConversationState, target_param="agg_inputs"):
    user_input = await state.user_input()  # not actually waiting
    state.memory[target_param] = state.memory.get(target_param, []) + [user_input]


async def oneliner_fallback(state, user_input):
    await state.say("Sorry I didn't get this")


async def example(state):
    await oneturn_say(state)
    with OutOfContext(state, oneliner_fallback):
        await oneturn_followup(state)


class Branch(BaseModel):
    branch_id: str
    intent_name: Optional[str]
    keywords: Optional[List[str]]


async def navigation(
    state: ConversationState, user_input=None, branches: List[Branch] = [], **kwargs
):
    user_input = user_input or await state.user_input()

    classic_intent_names = list(
        map(
            lambda b: b.get("intent_name"),
            filter(lambda b: "intent_name" in b and b["intent_name"]not in available_intents, branches),
        )
    )

    classic_intents_results = await coco_sdk.query_intents(
        intent_names=classic_intent_names, query=user_input
    )

    classic_intents_map = {r.name: r.result for r in classic_intents_results}

    for branch in branches:
        b = Branch.validate(branch)
        if (
            b.intent_name
            and b.intent_name in available_intents
            and available_intents[b.intent_name](user_input)
        ):
            return Outputs(control=b.branch_id)
        elif b.intent_name and classic_intents_map.get(b.intent_name):
            return Outputs(control=b.branch_id)
        if b.keywords and Intent(
            Pattern(WILDCARD, clean_keywords(b.keywords), WILDCARD)
        )(user_input):
            return Outputs(control=b.branch_id)

    await state.out_of_context(user_input)
