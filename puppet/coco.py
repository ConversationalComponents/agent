from coco.async_api import ComponentSession

async def coco(state, component_id, user_input=None):
    component_session = ComponentSession(component_id, state.session_id)
    if not user_input:
        user_input = await state.user_input()
    component_response = await component_session(user_input)
    while not component_response.component_done:
        await state.say(component_response.response)
        user_input = await state.user_input()
        component_response = await component_session(user_input)
    if component_response.response:
        await state.say(component_response.response)

