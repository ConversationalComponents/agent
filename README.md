[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/ConversationalComponents/puppet)

# Agent (agt)
Agent is a high-level toolkit for building chatbots using conversational components.
Try Agent if you want to make your chatbot modular using composable components.

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Channels](#channels)
- [NLU](#basic-language-understanding)

## Installation
```bash
# optional: create a virtual environment
python3 -m venv myvenv
source myvenv/bin/activate

# install agt
pip3 install agt
```
#### Additional dependecies
You may want to install dependencies to connect to channels such as telegram and discord or share components on cocohub.

Available dependecies
- discord - to connect your bot/component to discord
- telegram - to connect your bot/component to telegram
- msbf - to connect your bot/component to microsoft bot framework
- vendor - publish component on cocohub
- dsl - Hy DSL for nicer syntax when building components/nlu

Examples:
```bash
pip install agt[telegram]
# or for multiple dependecies
pip install agt[telegram,dsl]
```

## Getting Started
### Create your first bot
Agent components are python coroutines (note the `async def`)

We take `state` as the first parameter - which is an object that allow us to interact with the environment the component/bot is running on
```python
async def mybot(state):
    # state.user_input() waits for the next user input
    user_input = await state.user_input()

    # state.say sends a response
    await state.say(user_input)
```

Paste this code in a file called example.py

### Try it in the terminal
```bash
python3 -m agt example.mybot
```

## Channels
Connecting to channels is easy and just requires using regular Agent components

### Telegram
Make sure to install agt with telegram support - `pip install agt[telegram]`

Create a new bot and get telegram token from Telegram botfather using this guide: https://core.telegram.org/bots#6-botfather
```bash
export TELEGRAM_TOKEN=<Your telegram bot token>
python3 -m agt.channels.telegram example.mybot
```

### Discord
Make sure to install agt with discord support - `pip install agt[discord]`

Create a new bot account and get a token using this guide:
https://discordpy.readthedocs.io/en/latest/discord.html
```bash
export DISCORD_KEY=<Your discord bot token>
python3 -m agt.channels.discord example.mybot
```

### Microsoft bot framework
Make sure to install agt with microsoft bot framework support - `pip install agt[msbf]`

```bash
export MicrosoftAppId=<Your bot Microsft App Id>
export MicrosoftAppPassword=<Your bot Microsoft App Password>
python3 -m agt.channels.msbf example.mybot
```


## Basic Language Understanding
Inside agt.nlu we have simple patterns to regex compiler to perform basic understanding tasks

Compile simple word patterns to regex

Some Examples:
```python
intent = Intent(
    Pattern("the", "boy", "ate", "an", "apple")
)
assert intent("the boy ate an apple") == True
assert intent("the boy ate an orange") == False

intent = Intent(
    Pattern("the", "boy", "ate", "an", AnyWords(min=1, max=1))
)
assert intent("the boy ate an apple") == True
assert intent("the boy ate an orange") == True

intent = Intent(
    Pattern("the", Words("boy", "girl"), "ate", "an", AnyWords(min=1, max=1))
)
assert intent("the boy ate an apple") == True
assert intent("the boy ate an orange") == True
assert intent("the girl ate an orange") == True
assert intent("the girl ate a banana") == False

intent = Intent(
    Pattern("the", ("boy", "girl"), "ate", WordsRegex(r"an?"), AnyWords(min=1, max=1))
)
assert intent("the boy ate an apple") == True
assert intent("the boy ate an orange") == True
assert intent("the girl ate an orange") == True
assert intent("the girl ate a banana") == True
assert intent("a nice boy ate an apple") == False

intent = Intent(
    Pattern(WILDCARD, Words("boy", "girl"), "ate", WordsRegex(r"an?"), AnyWords(min=1, max=1))
)
assert intent("a nice boy ate an apple") == True
```

`Pattern` takes sentence elements and translate each one to optmized regular expression.

`Intent` groups multiple patterns so if any of the patterns match the intent evals to `True`