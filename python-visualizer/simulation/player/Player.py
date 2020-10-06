from simulation.player.PlayerState import PlayerState


class Player(object):
    def __init__(self, player_id: int, initial_state: PlayerState):
        self.player_id = player_id
        self.current_state: PlayerState = initial_state
        self.next_action = None
        self.is_active = True

    def do_action_and_move(self):
        if self.next_action is None:
            self.is_active = False

        if not self.is_active:
            return

        self.current_state.do_action(self.next_action)

        if self.current_state.speed_is_valid():
            self.current_state = self.current_state.do_move()
        else:
            self.is_active = False

        self.next_action = None

    def to_dict(self):
        return {
            "x": self.current_state.position_y,
            "y": self.current_state.position_x,
            "direction": self.current_state.direction.name.lower(),
            "speed": self.current_state.speed,
            "active": self.is_active,
            "name": f'Player #{self.player_id}'
        }

    def copy(self):
        return Player(self.player_id, self.current_state.copy())
