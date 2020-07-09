# Puppet
Puppet is a high-level toolkit for building chatbots using conversational components.
Try puppet if you want to make your chatbot modular using composable components.

## Installation
```bash
# optional: create a virtual environment
python3 -m venv myvenv
source myvenv/bin/activate

# install puppet
pip3 install coco-puppet
```

## Create your first bot
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