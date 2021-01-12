import asyncio
import json
import time
from datetime import datetime, timedelta
import os
import websockets
import requests
from csv import writer

import config

def append_to_csv(file_name: str, elements):
    with open(file_name, 'a+', newline='') as write:
        csv_writer = writer(write)
        csv_writer.writerow(elements)


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

    if not os.path.exists(config.GAME_ANALYSIS_DIRECTORY_PATH):
        os.makedirs(config.GAME_ANALYSIS_DIRECTORY_PATH)

    board_size_file_name = config.GAME_ANALYSIS_DIRECTORY_PATH + "sizes" + ".csv"
    time_file_name = config.GAME_ANALYSIS_DIRECTORY_PATH + "times-" \
                     + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv"

    url = config.URL
    key = config.API_KEY

    async with websockets.connect(f"{url}?key={key}") as websocket:
        rounds = 0
        print("Waiting for initial state...", flush=True)

        while True:
            state_json = await websocket.recv()
            state = json.loads(state_json)

            if rounds == 0:
                print(f"board -- width: %d -- height: %d" % (state["width"], state["height"]))
                append_to_csv(board_size_file_name, [state["width"], state["height"]])
            rounds += 1

            if not state["running"]:
                break

            deadline = datetime.strptime(state["deadline"], '%Y-%m-%dT%H:%M:%SZ')
            available_millis = (deadline - transform_to_server_time(datetime.now())) / timedelta(milliseconds=1)
            print(f"\tavailable milliseconds: %d" % available_millis)
            append_to_csv(time_file_name, [int(available_millis)])

            action_json = json.dumps({"action": "change_nothing"})
            await websocket.send(action_json)


while True:
    try:
        asyncio.get_event_loop().run_until_complete(play())
    except Exception as e:
        print(e)
        print("Connection was interrupted!")
    time.sleep(5)
