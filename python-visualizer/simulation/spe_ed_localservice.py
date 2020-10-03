from simulation.player import Player


class LocalGameService:
    players = []

    def __init__(self, width: int, height: int, player_count: int):
        cell_count = width * height
        start_point_distance = cell_count // (player_count + 1)

        self.width = width
        self.height = height
        self.cells = [0]*cell_count
        self.round = 1

        for player_id in range(0, player_count):
            start_cell = start_point_distance * (player_id + 1)
            player = Player(player_id, start_cell % width, start_cell // width)
            self.cells[start_cell] = player.player_id
            self.players.append(player)

    def do_action(self, player: int, player_action):
        if self.players[player].next_action is None:
            self.players[player].next_action = player_action
        else:
            self.players[player].speed = 0

    def next_round(self) -> str:
        next_step_cells = []
        for player in self.players:
            # apply next_action
            if (player.speed == 0 or
                    player.next_action is None or
                    (player.next_action == Player.PlayerAction.SLOW_DOWN and player.speed == 1) or
                    (player.next_action == Player.PlayerAction.SPEED_UP and player.speed == 10)):
                player.speed = 0
                player.next_action = None
                next_step_cells.append([])
                continue
            elif player.next_action == Player.PlayerAction.TURN_LEFT:
                player.direction = Player.PlayerDirection.LEFT if player.direction == Player.PlayerDirection.UP else player.direction - 1
            elif player.next_action == Player.PlayerAction.TURN_RIGHT:
                player.direction = Player.PlayerDirection.UP if player.direction == Player.PlayerDirection.LEFT else player.direction + 1
            elif player.next_action == Player.PlayerAction.SLOW_DOWN:
                player.speed -= 1
            elif player.next_action == Player.PlayerAction.SPEED_UP:
                player.speed += 1

            jump = self.round % 6 == 0 and player.speed >= 3

            new_position_x = player.x_position
            new_position_y = player.y_position
            new_position_indices = []

            if player.direction == Player.PlayerDirection.UP:
                new_position_y = self.calculate_move(player.y_position, True, player.speed)
                for pos in range(player.y_position + 1, new_position_y):
                    new_position_indices.append(self.get_cell_index(player.x_position, pos))
            elif player.direction == Player.PlayerDirection.RIGHT:
                new_position_x = self.calculate_move(player.x_position, True, player.speed)
                for pos in range(player.x_position + 1, new_position_x + 1):
                    new_position_indices.append(self.get_cell_index(pos, player.y_position))
            elif player.direction == Player.PlayerDirection.DOWN:
                new_position_y = self.calculate_move(player.y_position, False, player.speed)
                for pos in range(new_position_y, player.y_position + 1):
                    new_position_indices.append(self.get_cell_index(player.x_position, pos))
            elif player.direction == Player.PlayerDirection.LEFT:
                new_position_x = self.calculate_move(player.x_position, False, player.speed)
                for pos in range(new_position_x + 1, player.x_position + 1):
                    new_position_indices.append(self.get_cell_index(pos, player.y_position))

            while jump and len(new_position_indices) > 2:
                new_position_indices.pop(1)

            next_step_cells.append(new_position_indices)
            player.next_action = None
            player.x_position = new_position_x
            player.y_position = new_position_y

            for pos in new_position_indices:
                if self.cells[pos] == 0:
                    self.cells[pos] = player.player_id
                else:
                    # Crash -> Dead
                    player.speed = 0
                    self.cells[pos] = -1
                    # if already other processed players passed this cell in this round -> Kill them
                    for player_id in range(0, player.player_id + 1):
                        if pos in next_step_cells[player_id]:
                            self.players[player_id].speed = 0

        self.round += 1

        # TODO: generate a JSON String with the current Game-Data.
        return "json"

    def get_cell_index(self, x_position: int, y_position: int) -> int:
        return y_position * self.width + x_position

    def calculate_move(self, position: int, move_forward: bool, speed: int) -> int:
        pass
