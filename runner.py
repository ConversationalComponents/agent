from .state import ConversationState

def get_response(entry, state: ConversationState) -> str:
    run_s = ConversationState()
    entry_iter = entry(run_s)
    for msg in state.log:
        if msg.speaker == "user":
            run_s.log_message("user", msg.text)
            run_s.log_message("bot", next(entry_iter, "end"))
    return run_s.log[-1].text
