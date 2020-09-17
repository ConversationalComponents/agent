from agt import ConversationState
from agt.state import Outputs
from coco.async_api import ComponentSession
from coco.coco import CoCoResponse


async def emit_responses(state: ConversationState, component_response: CoCoResponse):
    if hasattr(component_response, "responses") and component_response.responses:
        for resp in component_response.responses:
            await state.say(text=resp.get("text"), image_url=resp.get("image"))
        return
    if component_response.response:
        await state.say(component_response.response)


async def coco(state, component_id, user_input=None, context={}, **params):
    component_session = ComponentSession(component_id, state.session_id)

    if not user_input:
        user_input = await state.user_input()

    component_response = await component_session(
        user_input,
        context=context,
        parameters=params,
        flatten_context=True,
        source_language_code=state.memory.get("source_language_code"),
    )
    state.memory = {**state.memory, **component_response.updated_context}

    while not component_response.component_done:
        await emit_responses(state, component_response)

        if component_response.out_of_context:
            await state.out_of_context(state.last_user_input())
        user_input = await state.user_input()
        component_response = await component_session(
            user_input,
            context=context,
            parameters=params,
            flatten_context=True,
            source_language_code=state.memory.get("source_language_code"),
        )
        state.memory = {**state.memory, **component_response.updated_context}

    await emit_responses(state, component_response)

    return Outputs(
        success=not component_response.component_failed, **component_response.outputs
    )
