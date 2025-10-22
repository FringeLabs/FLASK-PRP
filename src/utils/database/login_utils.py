# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from ..database.login import *

class LOGIN_MANAGER_UTILS:

    def __init__(self):
        self.login_utils_db = login_utils_db
        self.login_db_manager = LOGIN_MANAGER()
        self.login_utils_db.create_index(
            "creation_time",
            expireAfterSeconds=1800  
        )

    def check_if_invite_valid(self, u_id: str):
        return self.login_utils_db.find_one({"u_id": str(u_id)})

    def add_new_invite(self, email: str, password: str, college: str, u_id: str):
        if self.login_db_manager.check_if_user_has_account(email):
            raise ValueError("User already has an account")
        if self.login_utils_db.find_one({"email": email}):
            raise ValueError("User already submitted request. Try again with another email or reset your password.")
        password = sha256_crypt.hash(str(password))
        invite_doc = {
            "u_id": str(u_id),
            "email": email,
            "password": password,
            "college": college,
            "creation_time": datetime.utcnow(),  
        }
        self.login_utils_db.insert_one(invite_doc)

        return True
    

    def accept_invite(self, u_id: str):
        user_info = self.check_if_invite_valid(u_id)
        if not user_info:
            raise ValueError("Invalid or expired invite. Please request a new one.")

        self.login_db_manager.add_new_login(
            user_info["email"],
            str(user_info["password"]),
            user_info["college"],
            user_info["creation_time"],
        )

        self.login_utils_db.delete_one({"u_id": u_id})
        return True
