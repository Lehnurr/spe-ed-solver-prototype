import json

from simulation.player import Player, PlayerDirection, PlayerAction


class LocalGameService:
    players = []

    def __init__(self, width: int, height: int, player_count: int):
        cell_count = width * height
        start_point_distance = cell_count // (player_count + 1)

        self.width = width
        self.height = height
        self.cells = [[0 for x in range(width)] for y in range(height)]
        self.round = 1

        for player_id in range(1, player_count + 1):
            start_cell = start_point_distance * player_id
            player = Player(player_id, start_cell % width, start_cell // width)
            self.cells[player.position[1]][player.position[0]] = player.player_id
            self.players.append(player)

    def do_action(self, player: int, player_action):
        if self.players[player - 1].next_action is None:
            self.players[player - 1].next_action = player_action
        else:
            self.players[player - 1].speed = 0

    def next_round(self) -> str:
        next_step_cells = []
        for player in self.players:
            # apply next_action
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

            while jump and len(new_path) > 2:
                new_path.pop(1)

            next_step_cells.append(new_path)
            player.next_action = None
            player.position = new_position

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

        game_data = {
            "width": self.width,
            "height": self.height,
            "cells": self.cells,
            "players": {player.player_id: player.to_dict() for player in self.players},
            "you": 1,
            "running": True,
            "deadline": ""
        }

        return json.dumps(game_data)
