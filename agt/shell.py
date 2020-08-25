import asyncio

import dotenv
import click
from aioconsole import ainput

from .state import ConversationState

dotenv.load_dotenv()


async def input_loop(s) -> None:
    while True:
        await s.put_user_input(await ainput())


async def console_output(text, *args, **kwargs):
    print(f"Bot: {text}")


async def bot_init(bot, *args, **kwargs) -> None:
    s = ConversationState(console_output)
    s.memory["user_id"] = "shelluser"
    await asyncio.gather(input_loop(s), bot(s, *args, **kwargs))


def bot_runner(bot, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot_init(bot, *args, **kwargs))


@click.group()
def cli():
    """
        agt CLI, test and deploy your projects
    """
    pass


@cli.command()
@click.argument("component")
def run(component):
    """
        Run an Agent COMPONENT in the shell for testing

        COMPONENT example - module_a.module_b:agent_func_name"
    """
    import importlib
    import sys

    sys.path.append(".")

    entry_package_name, entry_name = component.split(":")

    entry_package = importlib.import_module(entry_package_name)
    entry = getattr(entry_package, entry_name)

    bot_runner(entry)


@cli.command()
@click.option(
    "--config",
    default="component.yaml",
    help="component yaml config",
    type=click.Path(exists=True),
)
def deploy(config):
    """
        deploy an agent project to CoCoHub cloud
    """
    from agt.deploy import deploy

    asyncio.run(deploy(config))


@cli.command()
@click.argument("component")
@click.option(
    "--component_id",
    help="The component id under exchange /api/exchange/<component_id>",
    type=click.STRING,
)
@click.option(
    "--config",
    help="Default config for the component e.g. module:TEMPLATE_DICT (when calling /api/config/<component_id>)",
    type=click.STRING,
)
@click.option(
    "--port", default=8080, help="Port to serve the component on", type=click.INT,
)
def serve(component, component_id, config, port):
    """
    Serve on a local http server a component with cocohub exchange protocol
    component format is module:agt_comp_name
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
