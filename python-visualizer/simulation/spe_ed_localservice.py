from colorclass import Color
from aenum import Enum


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
        

        for player in self.players:
            if(player.speed == 0 or player.next_action == None)
                # Player is dead
                continue
            # donext action and transfer state in cell-list / player-objects
# draw full action if not speed > 10 or < 1
            

                

        # kill player that crashed because of the next action

        # generate a JSON String with the current Game-Data.

        for player in self.players:
            player.next_action = None
        return "json"
