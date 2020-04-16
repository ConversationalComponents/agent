import time
import asyncio

from sanic import Sanic
from sanic.response import json

from puppet.server import PuppetSessionsManager

class PuppetCoCoApp:

    def __init__(self) -> None:
        self.blueprints: dict = {}
        self.sanic_app = Sanic(__name__)
        self.puppet_session_mgr = PuppetSessionsManager()
        self.sanic_app.add_route(self.exchange, "/api/exchange/<component_id>/<session_id>", methods=["POST"])
        self.sanic_app.add_route(self.exchange, "/exchange/<component_id>/<session_id>", methods=["POST"])

    def blueprint(self, f):
        async def component(*args, **kwargs):
            return await f(*args, **kwargs)
        self.blueprints[f.__name__] = f
        return component

    def run(self, *args, **kwargs):
        self.sanic_app.run(*args, **kwargs)

    async def exchange(self, request, component_id, session_id):
        """
        Single exchange of user input with the bot.
        """
        start_time = time.perf_counter()

        json_data = request.json or {}

        if component_id not in self.blueprints:
            return json({"error": f"Component: {component_id} not found"}, status=400)
        bp = self.blueprints[component_id]

        sc = self.puppet_session_mgr.get_session(session_id, bp)

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