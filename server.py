import asyncio
import websockets
from json import loads, dumps, JSONDecodeError
from model import Model

async def serve(socket, path):
    req = await socket.recv()
    try:
        req = loads(req)
        if req.get("cmd") == "all":
            res = model.everything
        if req.get("cmd") == "search":
            res = model.similar(req.get("query") or "Ling is weird")
        elif req.get("cmd") == "node":
            res = model.doc(req.get("id"))
        else:
            res = {"resp": "err"}
        res = dumps(res)
        await socket.send(res)
    except JSONDecodeError:
        await socket.send(dumps({"resp": "err"}))

if __name__ == "__main__":
    model = Model("arxiv.json")
    server = websockets.serve(serve, "localhost", 2326, max_size=None)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
