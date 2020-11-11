from typing import Dict, List, Tuple

from analysis.enemy.Enemy import Enemy
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerDirection


class EnemyCollection:
    def __init__(self):
        self.players: Dict[int: Enemy] = {}
        self.cells = None

    def update(self, step_info: dict) -> List[Tuple[int, int]]:
        last_round_board = None
        new_occupied_cells = []

        if self.cells:
            Board.from_cells(self.cells)

        self.cells = step_info["cells"]

        decision_relevant_player_states = {player_id: player.current_state for player_id, player in
                                           self.players.items()}

        # Update all players
        for player_id, player_data in step_info["players"].items():
            self.players.setdefault(player_id, Enemy(player_id,
                                                     PlayerDirection[player_data["direction"].upper()],
                                                     player_data["speed"],
                                                     player_data["x"],
                                                     player_data["y"],
                                                     step_info["width"],
                                                     step_info["height"]
                                                     )
                                    ).update(player_data)
            new_occupied_cells += self.players[player_id].current_state.steps_to_this_point

        # recalculate_aggressiveness for all enemies
        for player in self.players.values():
            # only for active players and not for your own player
            if player.is_active and player.player_id != step_info["you"]:
                players_enemies = [v for k, v in decision_relevant_player_states.items() if k != player.player_id]
                player.recalculate_aggressiveness(players_enemies, last_round_board)

        return new_occupied_cells
