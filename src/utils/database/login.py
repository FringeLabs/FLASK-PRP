# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from ..database import *
from datetime import datetime
from passlib.hash import sha256_crypt

class LOGIN_MANAGER:

    def __init__(self):
        self.login_db = login_db

    def check_if_user_has_account(self, email: str):
        return self.login_db.find_one({"email": email})
    

    def login_verify(self, email: str, password):
        if not self.check_if_user_has_account(email):
            raise ValueError("User has no account.")
        get_password = self.login_db.find_one({"email": email})
        if get_password.get("password"):
            if sha256_crypt.verify(str(password), get_password.get('password')):
                
                return True
        return False


    def add_new_login(self, email: str, password: str, college: str, creation_time: datetime):
        if self.check_if_user_has_account(email):
            raise ValueError("User already has an account")
        self.login_db.insert_one({
            "email": email,
            "password": password,
            "college": college,
            "creation_time": creation_time,
        })
        return True

    def reset_password(self, email: str, new_password: str):
        if not self.check_if_user_has_account(email):
            raise ValueError("User has no account")
        try:
            self.login_db.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
            )
        finally:
            return True