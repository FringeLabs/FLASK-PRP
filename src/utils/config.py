# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from os import getenv
from dotenv import load_dotenv
import secrets

load_dotenv(".env")


class CONFIG(object):
    FLASK_APP_HOST: str = getenv("FLASK_APP_HOST")
    FLASK_APP_PORT: int = getenv("FLASK_APP_PORT", 8080)
    UPLOAD_FOLDER: str = getenv("UPLOAD_FOLDER", "tmp/uploads")
    SECRET_KEY: str = getenv(
        "SKEY", secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+")
    )
    MONGO_URI: str = getenv("MONGO_URI", None)
    EMAIL_ID = getenv("EMAIL_ID", None)
    EMAIL_PASSWORD = getenv("EMAIL_PASSWORD", None)
    REMOVE_TMP_FILE_ON_STARTUP = True if getenv("RTFOS", "false").lower() == "true" else False
    APP_URL = getenv("APP_URL", "https://prp-flask.vercel.app/")
    APP_NAME = getenv("APP_NAME", "Project_PRP")
    EMAIL_HOST = getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = getenv("EMAIL_PORT", 587)


if not CONFIG.MONGO_URI:
    print("This APP doesn't work without It. Sorry!")