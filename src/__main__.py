# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from src import *

if __name__ == "__main__":
    __version__ = "0.0.2"
    print("============= Starting UP =============")
    print(f"{CONFIG.APP_NAME} Server v{__version__}...")
    print("============= Powered By FringeLABS =============")
    app.run(CONFIG.FLASK_APP_HOST, CONFIG.FLASK_APP_PORT)
