import logging
import os
import time
import asyncio

import traceback

from typing import Optional

import httpx
from sanic import Sanic
from sanic.response import json

from agt.server import AgentSessionsManager
from agt.state import Outputs

COCOHUB_URL = os.environ.get("COCOHUB_URL", "https://cocohub.ai")

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().addHandler(logging.FileHandler(filename="cocohub-agt.log"))


async def fetch_component_config(component_id: str) -> Optional[dict]:
    async with httpx.AsyncClient() as http_client:
        rv = await http_client.get(
            f"{COCOHUB_URL}/api/fetch_component_config/{component_id}"
        )
    resp_json: dict = rv.json()  # type: ignore
    return resp_json if "error" not in resp_json else None


class AgentCoCoApp:
    def __init__(self) -> None:
        self.blueprints: dict = {}
        self.blueprints_configs: dict = {}
        self.sanic_app = Sanic(__name__)
        self.agent_session_mgr = AgentSessionsManager()
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

    def blueprint(self, f, config=None, component_id=None):
        async def component(*args, **kwargs):
            return await f(*args, **kwargs)

        self.add_blueprint(f, component_id=component_id, config=config)
        return component

    def add_blueprint(self, f, config=None, component_id=None):
        component_id = component_id or f.__name__
        self.blueprints[component_id] = f
        if config:
            self.blueprints_configs[component_id] = config

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
        elif session_id not in self.agent_session_mgr.sessions:
            config = await fetch_component_config(blueprint_id)
            if not config:
                return json(
                    {"error": f"Blueprint: {blueprint_id} not found"}, status=400
                )
            config["component_id"] = blueprint_id
            blueprint_id = config["blueprint_id"]

            bp = self.blueprints[blueprint_id]
        else:
            bp = None

        async def wrapped_bp(*args, **kwargs):
            if config:
                kwargs["config"] = config
            try:
                return await bp(*args, **json_data.get("parameters", {}), **kwargs)
            except Exception as e:
                logging.exception(e)
                return Outputs(
                    success=False, error=traceback.format_exception_only(type(e), e)
                )

        sc = self.agent_session_mgr.get_session(session_id, wrapped_bp)

        if len(sc.out_of_context_input_event._waiters) > 0:
            sc.out_of_context_input_event.set()

        if "source_language_code" in json_data:
            sc.conv_state.memory["source_language_code"] = json_data[
                "source_language_code"
            ]

        sc.conv_state.memory.update(json_data.get("context", {}))

        await sc.conv_state.put_user_input(json_data.get("user_input", ""))

        await asyncio.wait(
            [sc.conv_state.bot_listen(), sc.bot_task, sc.wait_for_out_of_context()],
            return_when=asyncio.FIRST_COMPLETED,
        )

        outputs = Outputs()
        if sc.bot_task.done():
            result = sc.bot_task.result()
            if result:
                outputs = result

        eresp = {
            "responses": [{"text": r} for r in sc.responses],
            "response": sc.collect_responses(),
            "component_done": sc.bot_task.done(),
            "component_failed": sc.bot_task.done() and not outputs.success,
            "out_of_context": sc.out_of_context_event.is_set(),
            "updated_context": sc.conv_state.memory,
            "outputs": outputs.outputs,
        }

        sc.out_of_context_event.clear()

        eresp["response_time"] = time.perf_counter() - start_time
        return json(eresp)

    async def config(self, request, blueprint_id):
        return json(
            self.blueprints_configs.get(blueprint_id, {"blueprint_id": blueprint_id}),
        )
