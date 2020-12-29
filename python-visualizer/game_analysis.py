import asyncio
import json
import random
from datetime import datetime, time, timedelta

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

# async def play():
#     url = config.URL
#     key = config.API_KEY
#
#     game_board_viewer = None
#
#     async with websockets.connect(f"{url}?key={key}") as websocket:
#         print("Waiting for initial state...", flush=True)
#         while True:
#             state_json = await websocket.recv()
#             state = json.loads(state_json)
#             print("<", state)
#             action_json = json.dumps({"action": "change_nothing"})
#             await websocket.send(action_json)
#
#
# while True:
#     asyncio.get_event_loop().run_until_complete(play())
