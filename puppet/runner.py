from .state import ConversationState

def exchange(run_func, state: ConversationState, user_input: str) -> str:
    state.log_message("user", user_input)
    response = run_func(state, user_input)
    state.log_message("bot", response)
    return response
