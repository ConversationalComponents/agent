import agt
from agt.std.eliza import eliza_fallback

from agt.cocohub_vendor import AgentCoCoApp

app = AgentCoCoApp()


@app.blueprint
async def eliza_pv1(state):
    user_input = await state.user_input()
    await eliza_fallback(state, user_input)


@app.blueprint
async def echo(state):
    user_input = await state.user_input()
    await state.say(user_input)


@app.blueprint
async def namer_vp3(state):
    await agt.coco(state, "namer_vp3")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
