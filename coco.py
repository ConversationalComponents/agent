import requests

def coco_exchange(component_id, session_id, **kwargs):
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
    return requests.post(
        "https://app.coco.imperson.com/api/exchange/"
        f"{component_id}/{session_id}",
        json=kwargs,
    ).json()

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
            component_done = coco_data.get("component_done")
            component_failed = coco_data.get("component_failed")
            yield coco_data.get("response", "")
