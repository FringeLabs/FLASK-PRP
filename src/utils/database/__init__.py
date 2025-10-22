# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from pymongo import MongoClient
from ..config import CONFIG
import dns.resolver

try:
    dns.resolver.resolve("www.google.com")
except Exception:
    print("Resolving DNS. Setting to : 8.8.8.8")
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

db_client = MongoClient(CONFIG.MONGO_URI)

db_client.server_info()
print("Database working normally!")

main_db = db_client[f'PROJECT_{CONFIG.APP_NAME}']
login_db = main_db['LOGIN_DB']
login_utils_db = main_db['LOGIN_UTILS']
password_reset_db = main_db['PASS_RESET']