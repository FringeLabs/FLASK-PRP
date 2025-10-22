# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

import smtplib
from email.mime.text import MIMEText
from ...utils.config import CONFIG

class EMAIL_HELPERS:
    def __init__(self):
        self.sender = CONFIG.EMAIL_ID

    def send_email(self, to, subject, body):
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self.sender
        msg["To"] = to
        msg["Subject"] = subject

        try:
            with smtplib.SMTP(CONFIG.EMAIL_HOST, CONFIG.EMAIL_PORT) as server:
                server.starttls()
                server.login(CONFIG.EMAIL_ID, CONFIG.EMAIL_PASSWORD)
                server.sendmail(self.sender, to, msg.as_string())
                print(f"Email sent to {to}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            return str(e)

    def prepare_invite(self, mail, u_id):
        text_to_send = f"""Hello,

This is an automated email for verification of your {CONFIG.APP_NAME} account.
Click on the link to verify your email:
{CONFIG.APP_URL}/verify_user?u_id={u_id}

If you did not request this, please ignore this email.
"""
        self.send_email(mail, f"EMAIL VERIFICATION FOR {CONFIG.APP_NAME}", text_to_send)

    def prepare_reset(self, mail, u_id):
        """Send password reset link to the user's email."""
        text_to_send = f"""Hello,

You requested to reset your {CONFIG.APP_NAME} account password.
Click on the link below to reset your password:
{CONFIG.APP_URL}/pw_reset?u_id={u_id}

If you did not request this, please ignore this email.
"""
        self.send_email(mail, f"PASSWORD RESET FOR {CONFIG.APP_NAME}", text_to_send)
