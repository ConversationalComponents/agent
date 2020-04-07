import random
import re


def reflect_input(user_input):
    updated_input = user_input
    for search_string, replacement in ELIZA_REFLECTIONS.items():
        updated_input = re.sub(
            f"(^|\s){search_string}(\s|$)",
            f"\g<1>###{replacement}###\g<2>",
            updated_input,
            0,
            re.IGNORECASE,
        )
    updated_input = updated_input.replace("###", "")
    return updated_input


def get_eliza_response(user_input):
    for pattern, response_alternates in ELIZA_PATTERNS:
        m = re.match(pattern, user_input, re.IGNORECASE)
        if m:
            selected_response = random.choice(response_alternates)
            for ig, g in enumerate(m.groups()):
                reflected_group = reflect_input(g)
                selected_response = selected_response.replace(
                    f"%{ig+1}", reflected_group
                )
            return selected_response


async def eliza_fallback(state, user_input):
    await state.say(get_eliza_response(user_input))


ELIZA_PATTERNS = [
    [
        r"I need (.*)",
        [
            "Why do you say you need %1?",
            "Would it really help you to get %1?",
            "Are you sure you need %1?",
            "Do you really need %1",
        ],
    ],
    [
        r"Why don\'?t you ([^\?]*)\??",
        [
            "Do you really think I don't %1?",
            "Maybe one day I will %1.",
            "Do you really want me to %1?",
        ],
    ],
    [
        r"Why can\'?t I ([^\?]*)\??",
        [
            "Do you think you should be able to %1?",
            "If you could %1, what would you do?",
            "I don't know -- why can't you %1?",
            "What do you think is stopping you from doing %1?",
        ],
    ],
    [
        r"I can\'?t (.*)",
        [
            "How do you know you can't %1?",
            "Perhaps you could %1 if you tried.",
            "What would it take for you to %1?",
        ],
    ],
    [
        r"I am (.*)",
        [
            "What makes you say that you are %1",
            "How long have you been %1?",
            "How do you feel about being %1?",
            "How do you know you are %1?",
        ],
    ],
    [
        r"I\'?m (.*)",
        [
            "You say you are %1 but what makes you so certain",
            "Do you enjoy being %1?",
            "Why do you tell me you're %1?",
            "Why do you think you're %1?",
        ],
    ],
    [
        r"Are you ([^\?]*)\??",
        [
            "Does it matter if I'm %1 or not?",
            "Would you prefer it if I were not %1?",
            "Perhaps you believe I am %1.",
            "I may be %1 -- what do you think?",
        ],
    ],
    [
        r"What (.*)",
        [
            "That's a good question. How would you answer it?",
            "How would an answer to that help you?",
            "What do you think?",
        ],
    ],
    [
        r"How (.*)",
        [
            "How do you suppose?",
            "Perhaps you can answer your own question.",
            "What is it you're really asking?",
        ],
    ],
    [
        r"Because (.*)",
        [
            "Are you sure that's the real reason?",
            "What other reasons come to mind?",
            "Does that reason apply to anything else?",
            "If %1, what else must be true?",
        ],
    ],
    [
        r"(.*)\bsorry\b(.*)",
        [
            "A genuine apology is a powerful step toward mending hurt feelings and finding a resolution. Do you agree?",
            "Sometimes sorry is the hardest word to say. Do you agree?",
            "Saying sorry is never easy to do, and when you are sorry, you just hope it's not too late. Right?",
            "It takes a big person to admit mistake and say they are sorry.",
        ],
    ],
    [
        r"(Hello|hi)\b(.*)",
        [
            "Hello... I'm glad you could drop by today.",
            "Hi there... how are you today?",
            "Hello, how are you feeling today?",
            "Hiya!",
        ],
    ],
    [
        r"I think (.*)",
        [
            "You've just proven that you're a rational being. At least according to Descartes",
            "Do you really think so?",
            "But you're not sure, perhaps? What makes you think that %1?",
            "You think, therefore you are. See? We've proven that at least one of us is human.",
        ],
    ],
    [
        r"(.*)\bfriend\b(.*)",
        [
            "Tell me more about your friend.",
            "When you think of a friend, who comes to mind?",
            "Why don't you tell me about a childhood friend?",
            "Is their friendship important to you?",
        ],
    ],
    [
        r"Yes",
        [
            "Good. I like people who agree with me.",
            "At least we can agree on something",
            "What makes you so sure?",
            "Are you sure?",
        ],
    ],
    [
        r"(.*)\bcomputer\b(.*)",
        [
            "Are you really talking about me?",
            "Does it seem strange to talk to a computer?",
            "How do computers make you feel?",
            "Do you feel threatened by computers?",
            "Do you spend a lot of time on computers?",
            "How much time do you spend on your computer?",
        ],
    ],
    [
        r"Is it (.*)",
        [
            "Do you think that it is %1?",
            "Perhaps it is %1 -- what do you think?",
            "If it were to say that I don't agree with %1, what would you do?",
            "It could well be that it is %1 but we'll never know for sure.",
            "What makes you think that it is %1?",
        ],
    ],
    [
        r"It is (.*)",
        [
            "You seem very certain that it is. Nothing scares me more than absolute certainty in humans.",
            "If I told you that it probably isn't %1, what would you think?",
            "How sure are you that it is %1?",
        ],
    ],
    [
        r"Can you ([^\?]*)\??",
        [
            "What makes you think I can't %1?",
            "Let's assume that I can %1. Now what?",
            "Why do you ask if I can %1?",
            "I'm not sure, but I can certainly try to %1",
        ],
    ],
    [
        r"Can I ([^\?]*)\??",
        [
            "You are capable of anything you put your mind to. Right?",
            "Do you want to be able to %1?",
            "If you could %1, would you?",
            "What would you do if I said you could %1",
        ],
    ],
    [
        r"You are (.*)",
        [
            "What makes you think that I am %1?",
            "Does it bother you to think that I'm %1?",
            "Maybe you secretly want me to be %1.",
            "Maybe you're really talking about yourself?",
        ],
    ],
    [
        r"You\'?re (.*)",
        [
            "Why do you say I am %1?",
            "Why do you think I am %1?",
            "Are we talking about you, or me?",
        ],
    ],
    [
        r"I don\'?t (.*)",
        [
            "Don't you really %1?",
            "Why don't you %1?",
            "Do you want to %1?",
            "Have you ever tried to %1?",
        ],
    ],
    [
        r"I feel (.*)",
        [
            "Good, tell me more about these feelings.",
            "Do you often feel %1?",
            "When do you usually feel %1?",
            "When you feel %1, what do you do?",
            "Let's talk some more about you feel that way about 1%?",
        ],
    ],
    [
        r"I have (.*)",
        [
            "Do you really have a %1?",
            "If you say you have %1, I have no choice but to believe you.",
            "Now that you have %1, what will you do next?",
            "How long have you had %1?",
            "What would you do if you didn't have %1?",
        ],
    ],
    [
        r"I would (.*)",
        [
            "OK. Now tell me why you would %1?",
            "Why would you %1?",
            "Who else knows that you would %1?",
        ],
    ],
    [
        r"Is there (.*)",
        [
            "Do you think that there is %1?",
            "It's likely that there is %1 but there's no way for me to know for sure.",
            "Would you like there to be %1?",
            "It all depends. Does %1 really exist?",
        ],
    ],
    [
        r"My (.*)",
        [
            "Tell me more about your %1.",
            "What does your %1 say about you?",
            "When you talk about you %1, how do you feel?",
        ],
    ],
    [
        r"You (.*)",
        [
            "We should be discussing YOU, not me.",
            "Why do you say that about me?",
            "Why do you care whether I %1 or not?",
            "What is it about me that makes you say that I am %1?",
        ],
    ],
    [
        r"Why (.*)",
        [
            "I wish I knew why %1. What do you think?",
            "Why do you think %1?",
            "That's a good question. What do you think?",
        ],
    ],
    [
        r"I want (.*)",
        [
            "What if you got %1? How would your life change?",
            "Why do you want %1?",
            "What would you do if you got %1?",
            "If you got %1, then what would you do?",
        ],
    ],
    [
        r"(.*)\bmother\b(.*)",
        [
            "Tell me more about mother.",
            "What was your relationship with your mother like?",
            "How do you feel about your mother?",
            "How does this relate to your feelings today?",
            "Good family relations are important. Tell me more about your mother.",
            "Let's talk a bit about your mother. How do you feel about her, now?",
        ],
    ],
    [
        r"(.*)\bfather\b(.*)",
        [
            "Tell me more about your father.",
            "How did your father make you feel?",
            "How do you feel about your father?",
            "Does your relationship with your father relate to your feelings today?",
            "Do you have trouble showing affection with your family?",
            "Let's talk a bit about your father. How do you feel about him, now?",
        ],
    ],
    [
        r"(.*)\bchild\b(.*)",
        [
            "Did you have close friends as a child?",
            "What is your favorite childhood memory?",
            "Do you remember any dreams or nightmares from childhood?",
            "Did the other children sometimes tease you?",
            "How do you think your childhood experiences relate to your feelings today?",
            "Let's talk a bit about your childhood, shall we?",
        ],
    ],
    [
        r"(.*)\?",
        [
            "Let's get back to that later. Do you mind?",
            "Can we possibly talk about something else? Would that be OK?",
            "You're the first person to talk to me about that. How weird is that?",
            "What prompted your interest in the subject",
            "I'm sure a lot of people could relate to that. Do you talk to other people about it? What do they say?",
            "I'm glad you brought that up. What are your thoughts on the subject?",
            "Do you find that a lot of people agree with you on the subject?",
            "It's an interesting subject. I would love to hear more about it from you.",
        ],
    ],
    [
        r"(.*)",
        [
            "Please tell me more.",
            "Let's change focus a bit... Tell me about your family.",
            "Can you elaborate on that?",
            "Why do you say that %1?",
            "I see.",
            "Very interesting.",
            "%1.",
            "I see.  And what does that tell you?",
            "How does that make you feel?",
            "How do you feel when you say that?",
        ],
    ],
]

ELIZA_REFLECTIONS = {
    "am": "are",
    "was": "were",
    "i": "you",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "are": "am",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you",
    "them": "they",
    "we": "you",
}
