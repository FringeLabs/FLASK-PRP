# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from ..database.login import *
from passlib.hash import sha256_crypt
from datetime import datetime

class PASSWORD_RESET_UTILS:

    def __init__(self):
        self.reset_utils_db = password_reset_db  
        self.login_db_manager = LOGIN_MANAGER()
        self.reset_utils_db.create_index(
            "creation_time",
            expireAfterSeconds=1800 
        )

    def check_if_reset_valid(self, u_id: str):
        """Check if a password reset request exists and is valid."""
        return self.reset_utils_db.find_one({"u_id": str(u_id)})

    def add_reset_request(self, email: str, u_id: str):
        """Add a new password reset request if user exists."""
        if not self.login_db_manager.check_if_user_has_account(email):
            raise ValueError("No account associated with this email.")
        if self.reset_utils_db.find_one({"email": email}):
            raise ValueError("A reset request already exists. Please check your email.")
        
        reset_doc = {
            "u_id": str(u_id),
            "email": email,
            "creation_time": datetime.utcnow()
        }
        self.reset_utils_db.insert_one(reset_doc)
        return True

    def accept_reset(self, u_id: str, new_password: str):
        """Reset the user's password and remove the reset request."""
        reset_info = self.check_if_reset_valid(u_id)
        if not reset_info:
            raise ValueError("Invalid or expired reset request. Please request again.")
        
        hashed_password = sha256_crypt.hash(str(new_password))
        self.login_db_manager.reset_password(
            reset_info["email"],
            hashed_password
        )
        self.reset_utils_db.delete_one({"u_id": u_id})
        return True
