""" conversation state definition """
import logging
import typing as ta
import uuid

from asyncio import Queue, Event

logger = logging.getLogger("agt")


def generate_session_id():
    return str(uuid.uuid4())


class Entry:
    def __init__(self, text: str = None, image_url: str = None):
        self.text = text
        self.image_url = image_url

    def __repr__(self):
        if self.image_url:
            return " #img#: ".join([self.text or "", self.image_url])
        return self.text or ""


class BotEntry(Entry):
    def __repr__(self):
        return f"BOT >> {super().__repr__()}"


class UserEntry(Entry):
    def __repr__(self):
        return f"USER >> {super().__repr__()}"


class ConversationState:
    def __init__(self, output_callback):
        self.output_callback = output_callback
        self.session_id: str = generate_session_id()
        self.log: ta.List[Entry] = []
        self.out_of_context_handlers = []
        self._inputs_queue = None
        self._bot_wait_for_input_event = Event()

        self.memory = {}

    async def say(self, text: str, image_url: str = None):
        """Utter text message

        Arguments:
            text {str} -- The text message
        """
        logger.debug(f"BOT:{self.session_id}: {text}")
        if image_url:
            logger.debug(f"BOT:{self.session_id}: {image_url}")
        self.log.append(BotEntry(text, image_url))
        await self.output_callback(text, image_url)

    async def put_user_input(self, user_input: str):
        if not self._inputs_queue:
            self._inputs_queue = Queue()

        await self._inputs_queue.put(user_input)

    async def user_input(self) -> str:
        """Get next user input / wait for it

        Returns:
            str -- The user input
        """
        if not self._inputs_queue:
            # lazy load queue
            self._inputs_queue = Queue()
        if self._inputs_queue.empty():
            self._bot_wait_for_input_event.set()
        user_input = await self._inputs_queue.get()
        logger.debug(f"USER:{self.session_id}: {user_input}")
        self.log.append(UserEntry(user_input))
        return user_input

    def last_user_input(self) -> ta.Optional[str]:
        last_user_input = next(
            filter(lambda e: isinstance(e, UserEntry), reversed(self.log)), None
        )
        if last_user_input:
            return last_user_input.text
        return None

    def set_out_of_context_handler(self, handler: ta.Callable):
        self.out_of_context_handlers.append(handler)

    def pop_out_of_context_handler(self):
        self.out_of_context_handlers.pop()

    async def out_of_context(self, user_input: str, *args, **kwargs):
        if len(self.out_of_context_handlers) > 0:
            await self.out_of_context_handlers[-1](self, user_input, *args, **kwargs)

    async def bot_listen(self):
        await self._bot_wait_for_input_event.wait()
        self._bot_wait_for_input_event.clear()


class OutOfContext:
    def __init__(self, state, handler):
        self.state = state
        self.state.set_out_of_context_handler(handler)

    def __enter__(self):
        return self.state

    def __exit__(self, type, value, traceback):
        self.state.pop_out_of_context_handler()


class Outputs:
    def __init__(self, success=True, **kwargs):
        self.success = success
        self.outputs = kwargs
