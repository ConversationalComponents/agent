import time
import asyncio

from sanic import Sanic
from sanic.response import json

import puppet
from puppet.server import PuppetSessionsManager
from puppet.std.eliza import eliza_fallback

app = Sanic(__name__)

puppet_session_mgr = PuppetSessionsManager()

async def eliza_comp(state):
    user_input = await state.user_input()
    await eliza_fallback(state, user_input)

async def namer_vp3(state):
    await puppet.coco(state, "namer_vp3")

blueprints = {
    "eliza_pv1": eliza_comp,
    "namer_vp3": namer_vp3
}

async def exchange(request, component_id, session_id):
    """
    Single exchange of user input with the bot.
    """
    start_time = time.perf_counter()

    json_data = request.json or {}

    bp = blueprints[component_id]

    sc = puppet_session_mgr.get_session(session_id, bp)

    await sc.conv_state.put_user_input(json_data.get("user_input", ""))
    
    await asyncio.wait(
        [
            sc.conv_state.bot_listen(),
            sc.bot_task
            ],
        return_when=asyncio.FIRST_COMPLETED)
    
    eresp = {
        "response": sc.collect_responses(),
        "component_done": sc.bot_task.done(),
        "component_failed": False,
        "out_of_context": False,
        "updated_context": {}
    }

    eresp["response_time"] = time.perf_counter() - start_time
    return json(eresp)

app.add_route(exchange, "/api/exchange/<component_id>/<session_id>", methods=["POST"])
app.add_route(exchange, "/exchange/<component_id>/<session_id>", methods=["POST"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)