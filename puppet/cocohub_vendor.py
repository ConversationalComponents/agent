import os
import time
import asyncio

import httpx
from sanic import Sanic
from sanic.response import json

from puppet.server import PuppetSessionsManager

CONFIG_SERVER = os.environ.get("COCO_CONFIG_SERVER", "https://cocohub.ai/")


async def fetch_component_config(component_id: str) -> dict:
    async with httpx.AsyncClient() as http_client:
        rv = await http_client.get(
            f"{CONFIG_SERVER}/api/fetch_component_config/{component_id}"
        )
    return rv.json()


class PuppetCoCoApp:
    def __init__(self) -> None:
        self.blueprints: dict = {}
        self.blueprints_configs: dict = {}
        self.sanic_app = Sanic(__name__)
        self.puppet_session_mgr = PuppetSessionsManager()
        self.sanic_app.add_route(
            self.exchange, "/api/exchange/<blueprint_id>/<session_id>", methods=["POST"]
        )
        self.sanic_app.add_route(
            self.exchange, "/exchange/<blueprint_id>/<session_id>", methods=["POST"]
        )
        self.sanic_app.add_route(
            self.config, "/api/config/<blueprint_id>", methods=["GET"]
        )
        self.sanic_app.add_route(self.config, "/config/<blueprint_id>", methods=["GET"])

    def blueprint(self, f, config=None):
        async def component(*args, **kwargs):
            return await f(*args, **kwargs)

        self.add_blueprint(f, config)
        return component

    def add_blueprint(self, f, config=None):
        self.blueprints[f.__name__] = f
        if config:
            self.blueprints_configs[f.__name__] = config

    def run(self, *args, **kwargs):
        self.sanic_app.run(*args, **kwargs)

    async def exchange(self, request, blueprint_id, session_id):
        """
        Single exchange of user input with the bot.
        """
        start_time = time.perf_counter()

        json_data = request.json or {}

        if blueprint_id not in self.blueprints:
            return json({"error": f"Blueprint: {blueprint_id} not found"}, status=400)

        bp = self.blueprints[blueprint_id]

        config_id = json_data.get("config_id")

        if config_id and session_id not in self.puppet_session_mgr.sessions:
            config = (await fetch_component_config(config_id)).get(blueprint_id, {})
        else:
            config = self.blueprints_configs[blueprint_id]

        async def include_config_bp(*args, **kwargs):
            await bp(*args, config=config, **kwargs)

        sc = self.puppet_session_mgr.get_session(session_id, include_config_bp)

        await sc.conv_state.put_user_input(json_data.get("user_input", ""))

        await asyncio.wait(
            [sc.conv_state.bot_listen(), sc.bot_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        eresp = {
            "responses": [{"text": r} for r in sc.responses],
            "response": sc.collect_responses(),
            "component_done": sc.bot_task.done(),
            "component_failed": False,
            "out_of_context": False,
            "updated_context": {},
        }

        eresp["response_time"] = time.perf_counter() - start_time
        return json(eresp)

    async def config(self, request, blueprint_id):
        return json(
            {
                "blueprint_id": blueprint_id,
                blueprint_id: self.blueprints_configs.get(blueprint_id, {}),
            }
        )
