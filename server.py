from aiohttp import ClientSession, web


async def posthandler(request):
    data = await request.json()
    async with ClientSession().ws_connect("http://127.0.0.1:8080/") as ws:
        await ws.send_str(data["news"])
        await ws.close()
    return web.Response(status=200)


async def wshandler(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open("websocket.html", "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome!!!")

    try:
        print("Someone joined.")
        #for ws in request.app["sockets"]: #
        #    await ws.send_str("Someone joined") #
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        #for ws in request.app["sockets"]: 
        #    await ws.send_str("Someone disconnected.") 


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close() 


def main():
    app = web.Application()
    app["sockets"] = []
    app.router.add_route("GET", "/", wshandler) 
    app.router.add_route("POST", "/news", posthandler) 
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="127.0.0.1", port="8080")


if __name__ == "__main__":
    main()
