import asyncio
import typer
import pathlib
import json
import logging

from typing import Optional

import dotenv
from aioconsole import ainput

from .state import ConversationState

dotenv.load_dotenv()

shell_app = typer.Typer(
    name="agt-shell-app", help="agt CLI, test and deploy your projects"
)


async def input_loop(s) -> None:
    while True:
        await s.put_user_input(await ainput())


async def console_output(text, *args, **kwargs):
    print(f"Bot: {text}")


async def bot_init(bot, *args, **kwargs) -> None:
    s = ConversationState(console_output)
    s.memory["user_id"] = "shelluser"
    async def wrap_bot(bot, *args, **kwargs):
        try:
            return await bot(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            raise e
    await asyncio.gather(input_loop(s), wrap_bot(bot, s, *args, **kwargs))


def bot_runner(bot, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot_init(bot, *args, **kwargs))


@shell_app.command()
def run(
    component: str = typer.Argument(
        ..., help="example - module_a.module_b:agent_func_name"
    ),
    config: pathlib.Path = typer.Option(
        None, help="A config json file to test with a config"
    ),
):
    """
    Run an Agent COMPONENT in the shell for testing
    """
    import importlib
    import sys

    sys.path.append(".")

    entry_package_name, entry_name = component.split(":")

    entry_package = importlib.import_module(entry_package_name)
    entry = getattr(entry_package, entry_name)

    config_data = None
    if config:
        with open(config, "r") as f:
            config_data = json.load(f)

    bot_runner(entry, config=config_data)


@shell_app.command()
def deploy(
    config: pathlib.Path = typer.Option(
        pathlib.Path("component.yaml"), help="component yaml configuration file path"
    )
):
    """
    Deploy an agent project to CoCoHub cloud according to yaml configuration
    """
    from agt.deploy import deploy

    asyncio.run(deploy(config, app_name=shell_app.info.name))


@shell_app.command()
def serve(
    component: str = typer.Argument(
        ..., help="component to serve - format is module:agt_comp_name"
    ),
    component_id: Optional[str] = typer.Option(
        None,
        "--component_id",
        "--component-id",
        help="Component id on cocohub if different from the Agent component name (/api/exchange/<component_id>)",
    ),
    config: Optional[str] = typer.Option(
        None,
        help="Optional config for the component to publish on the hub (/api/config/<component_id>)",
    ),
    port: int = typer.Option(
        8080, "--port", "-p", help="port to serve the component on"
    ),
):
    """
    Serve on a local http server a component with cocohub exchange protocol
    """
    import sys
    import importlib
    from agt.cocohub_vendor import AgentCoCoApp

    sys.path.append(".")

    agent_app = AgentCoCoApp()

    comp_module_path, comp_module_name = component.rsplit(":", maxsplit=1)
    comp_module = importlib.import_module(comp_module_path)
    comp = getattr(comp_module, comp_module_name)

    config_obj = None
    if config:
        config_module_path, config_module_name = config.rsplit(":", maxsplit=1)
        config_module = importlib.import_module(config_module_path)
        config_obj = getattr(config_module, config_module_name)

    agent_app.add_blueprint(comp, component_id=component_id, config=config_obj)

    agent_app.run(host="0.0.0.0", port=port)
