import asyncio
import websockets
from json import loads, dumps, JSONDecodeError
from model import Model

model = Model("arxiv.json")

async def get_data(query, arg=None):
    print(model.similar(query))

async def get_node(id):
    pass

async def hello(socket, path):
    req = await socket.recv()
    try:
        req = loads(req)
        if req.get("cmd") == "fetchData":
            res = dumps(list(map(float, model.similar(req.get("query") or "Ling is weird"))))
        elif req.get("cmd") == "getNode":
            res = dumps(model.doc(req.get("id")))
        else:
            res = dumps({"resp": "err"})
        await socket.send(res)
    except JSONDecodeError:
        await socket.send(dumps({"resp": "err"}))

server = websockets.serve(hello, "localhost", 2326)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
