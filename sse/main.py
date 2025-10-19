# For tags
import random
from asyncio import sleep

import air

app = air.Air()


@app.page
def index():
    return air.layouts.mvpcss(
        air.Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
        air.Title("Server Sent Event Demo"),
        air.H1("Server Sent Event Demo"),
        air.P("Lottery number generator"),
        air.Section(
            hx_ext="sse",
            sse_connect="/lottery-numbers",
            # hx_swap="beforeend show:bottom",
            hx_swap="innerHTML",
            sse_swap="message",
        ),
    )

async def lottery_generator():
    while True:
        lottery_numbers = ", ".join([str(random.randint(1, 40)) for x in range(6)])
        # Tags work seamlessly
        yield air.Aside(lottery_numbers)
        # As do strings. Non-strings are cast to strings via the str built-in
        # yield "Hello, world"
        await sleep(1)


@app.get("/lottery-numbers")
async def get():
    return air.SSEResponse(lottery_generator())
