import json
import threading
import time
from datetime import datetime, timedelta

from Event import Event
from config import SIMULATION_DEADLINE

from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerDirection
from game_data.player.Player import Player


class LocalGameService:
    def __init__(self, width: int, height: int, player_count: int):

        self.board = Board(width, height)

        start_point_distance = self.board.cell_count // (player_count + 1)
        self.players = []

        # Init Player
        for player_id in range(1, player_count + 1):
            start_cell = start_point_distance * player_id
            player = Player(player_id,
                            PlayerState(PlayerDirection.LEFT, 1, start_cell % width, start_cell // self.board.width))
            self.board.set_cell(player.current_state.position_x, player.current_state.position_y, player.player_id)
            self.players.append(player)

        self.is_started = False
        self.deadline = None
        self.on_round_start = Event()
        self.all_player_moved = False

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
            self.players[player - 1].is_active = False

        if self.__is_running() and all(not p.is_active or p.next_action is not None for p in self.players):
            self.all_player_moved = True

    def __notify_player(self):
        self.on_round_start.notify(json.dumps({
            "width": self.board.width,
            "height": self.board.height,
            "cells": self.board.cells,
            "players": {player.player_id: player.to_dict() for player in self.players},
            "you": 1,
            "running": self.__is_running(),
            "deadline": self.deadline.replace(microsecond=0).isoformat("T") + "Z"
        }))

    def __reset_deadline(self):
        if SIMULATION_DEADLINE:
            self.deadline = datetime.utcnow() + timedelta(seconds=SIMULATION_DEADLINE)

    def __is_running(self) -> bool:
        return self.is_started and sum(p.is_active for p in self.players) > 1

    # is running in extra thread: checks the deadline and ends round
    def __wait_and_end_round(self):
        while self.__is_running():
            time.sleep(0.1)

            if self.all_player_moved or self.deadline and self.deadline < datetime.utcnow():
                self.__reset_deadline()

                for player in self.players:
                    if player.is_active:
                        player.do_action_and_move()
                        for point in player.current_state.steps_to_this_point:
                            self.board.set_cell(point[0], point[1], player.player_id)
                        player.is_active &= player.current_state.verify_state(self.board)

                for player in self.players:
                    if player.is_active:
                        for point in player.current_state.steps_to_this_point:
                            if self.board[point[1]][point[0]] == -1:
                                player.is_active = False

                self.all_player_moved = False
                self.__notify_player()
