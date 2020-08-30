import asyncio

from .state import ConversationState


class BotSessionContainer:
    def __init__(self, bot_coro, async_output_callback=None):
        event_loop = asyncio.get_event_loop()
        self.responses = []
        self.conv_state = ConversationState(async_output_callback or self.add_response)
        self.bot_task: asyncio.Task = event_loop.create_task(bot_coro(self.conv_state))

    async def add_response(self, text, *args, **kwargs):
        self.responses.append(text)

    def collect_responses(self):
        response = " ".join(self.responses)
        self.responses = []
        return response


class AgentSessionsManager:
    def __init__(self):
        self.sessions = {}

    def session_cleanup_builder(self, bot, session_id):
        async def bot_coro(s):
            res = None
            try:
                res = await bot(s)
            except Exception as e:
                raise e
            finally:
                self.sessions.pop(session_id, None)
            return res

        return bot_coro

    def get_session(
        self, session_id, bot, async_output_callback=None
    ) -> BotSessionContainer:
        sc = self.sessions.get(session_id)
        if not sc or (sc.bot_task.done() and sc.bot_task.exception()):
            sc = BotSessionContainer(
                self.session_cleanup_builder(bot, session_id),
                async_output_callback=async_output_callback,
            )
            self.sessions[session_id] = sc
        return sc
