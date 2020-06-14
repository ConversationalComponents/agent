from puppet.state import Outputs
from coco.async_api import ComponentSession


async def coco(state, component_id, user_input=None, context={}, **params):
    component_session = ComponentSession(component_id, state.session_id)

    if not user_input:
        user_input = await state.user_input()

    component_response = await component_session(
        user_input, context=context, params=params
    )
    while not component_response.component_done:
        await state.say(component_response.response)
        user_input = await state.user_input()
        component_response = await component_session(
            user_input, context=context, params=params
        )

    if component_response.response:
        await state.say(component_response.response)
    if component_response.component_failed:
        return Outputs(success=False)
