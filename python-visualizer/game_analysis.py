import asyncio
import json
import time
from datetime import datetime, timedelta

import websockets
import requests
from csv import writer

import config

client_time = datetime.now()
time_request_result = requests.get(config.TIME_URL)

if time_request_result.status_code != 200:
    print("Time API not available!")
    exit()

time_request_content = json.loads(time_request_result.content)

server_time = datetime.strptime(time_request_content["time"], '%Y-%m-%dT%H:%M:%SZ')
server_time += timedelta(milliseconds=time_request_content["milliseconds"])

time_offset = server_time - client_time
print(f"time offset to server: %s" % time_offset)


def transform_to_server_time(time_value: datetime):
    return time_value + time_offset

async def play():
    url = config.URL
    key = config.API_KEY

    async with websockets.connect(f"{url}?key={key}") as websocket:
        started = False
        print("Waiting for initial state...", flush=True)

        while True:
            state_json = await websocket.recv()
            state = json.loads(state_json)

            if not started:
                print(f"board -- width: %d -- height: %d" % (state["width"], state["height"]))
                started = True

            if not state["running"]:
                break

            deadline = datetime.strptime(state["deadline"], '%Y-%m-%dT%H:%M:%SZ')
            available_millis = (deadline - transform_to_server_time(datetime.now())) / timedelta(milliseconds=1)

            print(f"\tavailable milliseconds: %d" % available_millis)

            time.sleep(0.5)

            action_json = json.dumps({"action": "change_nothing"})
            await websocket.send(action_json)


while True:
    try:
        asyncio.get_event_loop().run_until_complete(play())
    except Exception:
        print("Connection was interrupted!")
