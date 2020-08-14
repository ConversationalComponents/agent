import click
import asyncio
from .state import ConversationState
from aioconsole import ainput


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
