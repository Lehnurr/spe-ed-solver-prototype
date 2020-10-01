from colorclass import Color
from aenum import Enum

PlayerAction = Enum('PlayerAction', 'turn_left turn_right slow_down speed_up change_nothing')
PlayerDirection = Enum('PlayerAction', 'left right up down')


class Player(object):

    def __init__(self, player_id: int, color: Color, x_position: int, y_position: int):
        self.player_id = player_id
        self.color = color
        self.x_position = x_position
        self.y_position = y_position
        self.speed = 1
        self.next_action = None
        self.direction = PlayerDirection.up


class LocalGameService:
    players = []

    def __init__(self, width: int, height: int, player_colors):
        cell_count = width * height
        start_point_distance = cell_count // (len(player_colors) + 1)

        self.width = width
        self.height = height
        self.cells = [0]*cell_count

        for index, color in enumerate(player_colors):
            start_cell = start_point_distance * (index + 1)
            player = Player(index, color, start_cell % width, start_cell // width)
            self.cells[start_cell] = player.player_id
            self.players.append(player)

    def do_action(self, player: int, player_action):
        if self.players[player].next_action is None:
            self.players[player].next_action = player_action
        else:
            self.players[player].speed = 0

    def next_round(self) -> str:
        # If speed = 0 or next_action = None -> Player is dead

        # do actions in seperated environment -> Check Player status (Speed, position on board, crashes, ...)
        # Detect new dead players and transfer new Data in the cell-List
        # generate a JSON String with the current Game-Data.
        # Implement after Issue https://github.com/informatiCup/InformatiCup2021/issues/5 is solved...

        for player in self.players:
            player.next_action = None
        return "json"
