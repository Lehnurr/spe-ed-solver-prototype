
# -------------------------------------------------------------------
# file for configuration default values
# values may be overwritten by an existing local configuration file
# -------------------------------------------------------------------

import os

URL = "wss://msoll.de/spe_ed"
API_KEY = 000000

# Types of players selected.
# The order in the array defines the priority of players.
SELECTED_PLAYER_TYPES = ["RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer"]

# Defines if the game is played online or simulated locally.
SIMULATED = True

# Value for the amount of players used in a simulation.
PLAYER_COUNT = 6

# Simulation dimensions.
SIMULATION_BOARD_WIDTH = 64
SIMULATION_BOARD_HEIGHT = 64


if os.path.exists(os.path.join(os.path.dirname(__file__), 'config_local.py')):
    from config_local import *
