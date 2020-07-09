# Puppet
Puppet is a high-level toolkit for building chatbots using conversational components.
Try puppet if you want to make your chatbot modular using composable components.

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Channels](#channels)

## Installation
```bash
# optional: create a virtual environment
python3 -m venv myvenv
source myvenv/bin/activate

# install puppet
pip3 install coco-puppet
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
pip install coco-puppet[telegram]
# or for multiple dependecies
pip install coco-puppet[telegram,dsl]
```

## Getting Started
### Create your first bot
Puppet components are python coroutines (note the `async def`)

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
python3 -m puppet example.mybot
```

## Channels
Connecting to channels is easy and just requires using regular puppet components

### Telegram
Make sure to install puppet with telegram support - `pip install coco-puppet[telegram]`
```bash
python3 -m puppet.channels.telegram example.mybot
```

### Discord
Make sure to install puppet with discord support - `pip install coco-puppet[discord]`
```bash
python3 -m puppet.channels.discord example.mybot
```

### Microsoft bot framework
Make sure to install puppet with microsoft bot framework support - `pip install coco-puppet[msbf]`
```bash
python3 -m puppet.channels.msbf example.mybot
```