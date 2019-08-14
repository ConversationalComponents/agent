from dataclasses import dataclass
import requests

@dataclass
class CoCoResponse:
    response: str
    component_done: bool
    updated_context: dict
    confidence: float
    idontknow: bool
    raw_resp: dict

def coco_exchange(component_id, session_id,
                  user_input=None, **kwargs) -> CoCoResponse:
    """
    calls coco and try to maintain similar api.
    available optional kwargs are:
        user_input
        context

    full api spec available at app.coco.imperson.com

    Arguments:
        component_id {str} -- the component id from coco app
        session_id {str} -- a randomly generated session id to identify the session

    Returns:
        {
            "response": str,
            "component_done": bool,
            "component_failed": bool,
            "updated_context": dict
        }
        dict -- response from coco
    """
    payload = kwargs
    if user_input:
        payload = {**{"user_input": user_input}, **kwargs}
    coco_resp = requests.post(
        "https://app.coco.imperson.com/api/exchange/"
        f"{component_id}/{session_id}",
        json=payload,
    ).json()
    return CoCoResponse(**coco_resp, raw_resp=coco_resp)

class ConvComp:
    def __init__(self, component_id):
        self.component_id = component_id

    def __call__(self, session_id, user_input=None, **kwargs):
        return coco_exchange(self.component_id, session_id, user_input, **kwargs)

class CocoPolicy:
    def __init__(self, component_id):
        self.component_id = component_id

    def __call__(self, state):
        component_done = False
        component_failed = False
        while not component_done:
            coco_data = coco_exchange(
                self.component_id,
                state.session_id,
                user_input=state.get_last_user_input().text,
                log_len=len(state.log),
                director_log=state.director_log
            )
            component_done = coco_data.component_done
            component_failed = coco_data.raw_resp.get("component_failed", False)
            yield coco_data.response
