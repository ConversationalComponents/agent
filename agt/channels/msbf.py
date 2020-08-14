import logging
import os
import sys
import importlib

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core import ActivityHandler, MessageFactory
from botbuilder.schema import Activity

from ..server import AgentSessionsManager

logging.basicConfig(filename="agt-msbf.log", level=logging.DEBUG)
PORT = os.environ.get("PORT", 3978)
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

sess_mgr = AgentSessionsManager()


class OutputCallback:
    def __init__(self, turn_context) -> None:
        self.turn_context = turn_context

    async def __call__(self, text, image_url=None, *args, **kwargs):
        if image_url:
            msg = MessageFactory.content_url(
                url=image_url, content_type="image/" + image_url[-3:], text=text
            )
        else:
            msg = MessageFactory.text(text)
        await self.turn_context.send_activity(msg)


class PuppetBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):

        session_id = turn_context.activity.conversation.id

        output_callback = OutputCallback(turn_context)

        sc = sess_mgr.get_session(session_id, entry, output_callback)

        sc.conv_state.memory["user_id"] = session_id

        await sc.conv_state.put_user_input(turn_context.activity.text)


# Create the Bot
BOT = PuppetBot()


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    _, entry_path, *args = sys.argv

    entry_package_name, entry_name = entry_path.rsplit(".", 1)

    entry_package = importlib.import_module(entry_package_name)
    entry = getattr(entry_package, entry_name)

    try:
        web.run_app(APP, host="localhost", port=PORT)
    except Exception as error:
        raise error
