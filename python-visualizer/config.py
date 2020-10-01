
# -------------------------------------------------------------------
# file for configuration default values
# values may be overwritten by an existing local configuration file
# -------------------------------------------------------------------

import os

URL = "wss://msoll.de/spe_ed"
API_KEY = 000000


if os.path.exists(os.path.join(os.path.dirname(__file__), 'config_local.py')):
    from config_local import *
