from dataclasses import dataclass
from coco import *

class CocoPolicy:
    def __init__(self, component_id):
        self.component_id = component_id

    def __call__(self, state):
        component_done = False
        component_failed = False
        while not component_done:
            coco_data = exchange(
                self.component_id,
                state.session_id,
                user_input=state.get_last_user_input().text
            )
            component_done = coco_data.component_done
            component_failed = coco_data.raw_resp.get("component_failed", False)
            yield coco_data.response
