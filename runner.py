from .state import ConversationState

def get_response(run_func, state: ConversationState, user_input) -> str:
    local_state = ConversationState(director_log=False)
    entry_iter = run_func(local_state)
    for msg in state.log:
        if msg.speaker == "user":
            local_state.log_message("user", msg.text)
            local_state.log_message("bot", next(entry_iter, "end"))
    local_state.session_id = state.session_id
    local_state.director_log = True
    local_state.log_message("user", user_input)
    response = next(entry_iter, "end")
    return response


def exchange(run_func, state: ConversationState, user_input: str) -> str:
    state.log_message("user", user_input)
    response = run_func(state, user_input)
    state.log_message("bot", response)
    return response
