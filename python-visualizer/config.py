
# -------------------------------------------------------------------
# file for configuration default values
# values may be overwritten by an existing local configuration file
# -------------------------------------------------------------------

import os


# Python recursion limit.
RECURSION_LIMIT = 10000

# Webservice
URL = "wss://msoll.de/spe_ed"
TIME_URL = "https://msoll.de/spe_ed_time"
API_KEY = 000000

# Types of players selected.
# The order in the array defines the priority of players.
SELECTED_PLAYER_TYPES = ["RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer", "RandomPlayer"]

# Defines if the game is played online or simulated locally.
SIMULATED = False

# Simulation parameters.
SIMULATION_PLAYER_COUNT = 4
SIMULATION_BOARD_WIDTH = 64
SIMULATION_BOARD_HEIGHT = 64

NOTIFY_SIMULATED_PLAYER_ASYNC = False
SIMULATION_DEADLINE = None

if os.path.exists(os.path.join(os.path.dirname(__file__), 'config_local.py')):
    from config_local import *

# game analysis paths
GAME_ANALYSIS_SIZE_PATH = "../.data/size"
GAME_ANALYSIS_TIME_PATH = "../.data/time"
