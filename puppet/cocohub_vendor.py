import os
import time
import asyncio

from typing import Optional

import httpx
from sanic import Sanic
from sanic.response import json

from puppet.server import PuppetSessionsManager

CONFIG_SERVER = os.environ.get("COCO_CONFIG_SERVER", "https://cocohub.ai/")


async def fetch_component_config(component_id: str) -> Optional[dict]:
    async with httpx.AsyncClient() as http_client:
        rv = await http_client.get(
            f"{CONFIG_SERVER}/api/fetch_component_config/{component_id}"
        )
    resp_json: dict = rv.json()  # type: ignore
    return resp_json if "error" not in resp_json else None


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

        config = None
        if blueprint_id in self.blueprints:
            bp = self.blueprints[blueprint_id]
        elif session_id not in self.puppet_session_mgr.sessions:
            config = await fetch_component_config(blueprint_id)
            if not config:
                return json(
                    {"error": f"Blueprint: {blueprint_id} not found"}, status=400
                )
            blueprint_id = config["blueprint_id"]

            bp = self.blueprints[blueprint_id]
        else:
            bp = None

        async def include_config_bp(*args, **kwargs):
            if config:
                kwargs["config"] = config
            return await bp(*args, **json_data.get("parameters", {}), **kwargs)

        sc = self.puppet_session_mgr.get_session(session_id, include_config_bp)

        await sc.conv_state.put_user_input(json_data.get("user_input", ""))

        await asyncio.wait(
            [sc.conv_state.bot_listen(), sc.bot_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        outputs = {}
        if sc.bot_task.done():
            result = sc.bot_task.result()
            if result:
                outputs = result.outputs

        eresp = {
            "responses": [{"text": r} for r in sc.responses],
            "response": sc.collect_responses(),
            "component_done": sc.bot_task.done(),
            "component_failed": False,
            "out_of_context": False,
            "updated_context": sc.conv_state.memory,
            "outputs": outputs,
        }

        eresp["response_time"] = time.perf_counter() - start_time
        return json(eresp)

    async def config(self, request, blueprint_id):
        return json(
            self.blueprints_configs.get(blueprint_id, {"blueprint_id": blueprint_id}),
        )
