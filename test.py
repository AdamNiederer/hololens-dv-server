import asyncio
import websockets
from json import dumps

async def test_fetch_data():
    async with websockets.connect('ws://localhost:2326') as websocket:
        await websocket.send(dumps({"cmd": "fetchData", "query": "Graph theory"}))
        print(await websocket.recv())

async def test_get_node():
    async with websockets.connect('ws://localhost:2326') as websocket:
        await websocket.send(dumps({"cmd": "getNode", "id": "arxiv_link_Here"}))
        print(await websocket.recv())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_fetch_data())
    asyncio.get_event_loop().run_until_complete(test_get_node())
