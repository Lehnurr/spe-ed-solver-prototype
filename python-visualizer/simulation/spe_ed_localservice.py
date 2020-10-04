import json
import threading
import time
from datetime import datetime, timedelta

from Event import Event
from simulation.player import Player, PlayerDirection, PlayerAction

DEADLINE_SECONDS = 10


class LocalGameService:
    def __init__(self, width: int, height: int, player_count: int):
        cell_count = width * height
        start_point_distance = cell_count // (player_count + 1)

        self.width = width
        self.height = height
        self.cells = [[0 for x in range(width)] for y in range(height)]
        self.round = 1
        self.players = []

        # Init Player
        for player_id in range(1, player_count + 1):
            start_cell = start_point_distance * player_id
            player = Player(player_id, start_cell % width, start_cell // width)
            self.cells[player.position[1]][player.position[0]] = player.player_id
            self.players.append(player)

        self.listeners = []
        self.is_started = False
        self.deadline = None
        self.on_round_start = Event()

    # Starts the Game and sends first Notification to the Player
    def start(self):
        self.is_started = True
        self.__reset_deadline()
        threading.Thread(target=self.__wait_and_end_round, args=()).start()
        self.__notify_player()

    # processes an User interaction
    def do_action(self, player: int, player_action):
        if not self.is_started:
            raise Exception('Game is not started')
        elif self.players[player - 1].next_action is None:
            self.players[player - 1].next_action = player_action
        else:
            self.players[player - 1].speed = 0

        if self.__is_running() and all(p.speed == 0 or p.next_action is not None for p in self.players):
            self.__next_round()

    # Performs player actions, evaluates the score, ends the round, starts a new round and notifies the players
    # is called automatically by the LocalGameService
    def __next_round(self):
        if not self.is_started:
            return

        self.__reset_deadline()
        next_step_cells = []

        for player in self.players:
            # Apply next_action
            if (player.speed == 0 or
                    player.next_action is None or
                    (player.next_action == PlayerAction.SLOW_DOWN and player.speed == 1) or
                    (player.next_action == PlayerAction.SPEED_UP and player.speed == 10)):
                player.speed = 0
                player.next_action = None
                next_step_cells.append([])
                continue
            elif player.next_action == PlayerAction.TURN_LEFT or player.next_action == PlayerAction.TURN_RIGHT:
                player.direction = player.direction.turn(player.next_action)
            elif player.next_action == PlayerAction.SLOW_DOWN:
                player.speed -= 1
            elif player.next_action == PlayerAction.SPEED_UP:
                player.speed += 1

            jump = self.round % 6 == 0 and player.speed >= 3

            new_position = player.position.copy()
            new_path = []

            # Move and calculate the passed Cells
            if player.direction == PlayerDirection.UP:
                new_position[1] = player.position[1] - player.speed
                for pos in range(new_position[1], player.position[1]):
                    new_path.append((player.position[0], pos))
            elif player.direction == PlayerDirection.RIGHT:
                new_position[0] = player.position[0] + player.speed
                for pos in range(player.position[0] + 1, new_position[0] + 1):
                    new_path.append((pos, player.position[1]))
            elif player.direction == PlayerDirection.DOWN:
                new_position[1] = player.position[1] + player.speed
                for pos in range(player.position[1] + 1, new_position[1] + 1):
                    new_path.append((player.position[0], pos))
            elif player.direction == PlayerDirection.LEFT:
                new_position[0] = player.position[0] - player.speed
                for pos in range(new_position[0], player.position[0]):
                    new_path.append((pos, player.position[1]))

            # Remove the jumped over cells
            while jump and len(new_path) > 2:
                new_path.pop(1)

            next_step_cells.append(new_path)
            player.next_action = None
            player.position = new_position

            # Apply new paths and check for new deaths
            for pos in new_path:
                if pos[0] < 0 or pos[0] >= self.width or pos[1] < 0 or pos[1] >= self.height:
                    # Out of Game field
                    player.speed = 0
                    break
                elif self.cells[pos[1]][pos[0]] == 0:
                    self.cells[pos[1]][pos[0]] = player.player_id
                else:
                    # Crash -> Dead
                    player.speed = 0
                    self.cells[pos[1]][pos[0]] = -1
                    # if already other processed players passed this cell in this round -> Kill them
                    for player_id in range(1, player.player_id):
                        if pos in next_step_cells[player_id - 1]:
                            self.players[player_id - 1].speed = 0

        self.round += 1
        self.__notify_player()

    def __notify_player(self):
        self.on_round_start.notify(json.dumps({
            "width": self.width,
            "height": self.height,
            "cells": self.cells,
            "players": {player.player_id: player.to_dict() for player in self.players},
            "you": 1,
            "running": self.__is_running(),
            "deadline": self.deadline.replace(microsecond=0).isoformat("T") + "Z"
        }))

    def __reset_deadline(self):
        remaining_seconds = DEADLINE_SECONDS
        self.deadline = datetime.utcnow() + timedelta(seconds=remaining_seconds)

    def __is_running(self) -> bool:
        return self.is_started and sum(p.speed > 0 for p in self.players) > 1

    # is running in extra thread: checks the deadline
    def __wait_and_end_round(self):
        while self.__is_running():
            time.sleep(1)
            if self.deadline < datetime.utcnow():
                self.__next_round()
