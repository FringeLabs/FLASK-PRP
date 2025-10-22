# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from .utils.parsers import TextParser
from .utils.pdf_utils import PDFParser
from flask import Flask, render_template, request, send_file, jsonify, session, redirect
from os import path as os_path
from .utils.config import *
import uuid
import json
from random import randint
from werkzeug.utils import secure_filename
from src import *
from os import makedirs
from .utils.database.login import LOGIN_MANAGER
from .utils.database.login_utils import LOGIN_MANAGER_UTILS
from .utils.email_helpers import *
from shutil import rmtree as rm_tree
from .utils.database.password_reset_utils import PASSWORD_RESET_UTILS
import threading
import contextlib

login_utils = LOGIN_MANAGER_UTILS()
login_client = LOGIN_MANAGER()
pass_utils = PASSWORD_RESET_UTILS()
email_client = EMAIL_HELPERS()

app = Flask(f"{CONFIG.APP_NAME}_SERVER", template_folder="templates", static_folder="static")
upload_to = CONFIG.UPLOAD_FOLDER
app.secret_key = CONFIG.SECRET_KEY

if CONFIG.REMOVE_TMP_FILE_ON_STARTUP:
    with contextlib.suppress(Exception):
        if os_path.exists(upload_to):
            rm_tree(upload_to)

excluded_paths = ["/static", "/login", "/login_page", "/templates", "/src", "/signup", "/password_reset", "/verify_user", "/signup_api", "/pw_reset", "/pw_reset_api"]


if not os_path.exists(upload_to):
    makedirs(upload_to)

def send_email_in_background(target_func, *args, **kwargs):
    thread = threading.Thread(target=target_func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()


    


@app.route("/signup")
def signup_page():
    if "username" in session:
        return redirect("/")
    return render_template("signup.html")


@app.route("/password_reset")
def pw_reset_page():
    if "username" in session:
        return redirect("/")
    return render_template("password_reset.html")


@app.route("/password_reset_api", methods=["POST"])
def pw_api():
    if "username" in session:
        return redirect("/")
    
    data = request.json
    print(data)
    if not all(data.get(k) for k in ["email"]):
        return jsonify({"error": "Please fill your email"}), 400

    u_id = str(uuid.uuid1())
    try:
        pass_utils.add_reset_request(email=data["email"], u_id=u_id)
        send_email_in_background(email_client.prepare_reset, data["email"], u_id)
    except Exception as e:
        print(e)
        return jsonify({"error": "Email already sent few minutes ago. Do not spam."}), 400

    return jsonify({"message": "Request submitted successfully"})


@app.route("/pw_reset", methods=["GET", "POST"])
def pw_reset_user():
    if "username" in session:
        return redirect("/")
    
    u_id = request.args.get("u_id")
    if not u_id:
        return jsonify({"error": "Missing or invalid u_id"}), 400

    if request.method == "POST":
        new_password = request.form.get("new_password")
        if not new_password:
            return jsonify({"error": "Please provide a new password"}), 400
        if len(new_password) < 8:
            return jsonify({"error": "Password too weak."})
        try:
            pass_utils.accept_reset(u_id=u_id, new_password=new_password)
        except ValueError:
            return jsonify({"error": "Unable to process request"}), 400
        return jsonify({"message":"Password reset successfully!"})
    reset_info = pass_utils.check_if_reset_valid(u_id)
    if not reset_info:
        return jsonify({"error": "Invalid or expired reset request"}), 400
    return render_template("password_reset_form.html", u_id=u_id)



@app.route("/signup_api", methods=["POST"])
def signup_api():
    if "username" in session:
        return redirect("/")
    data = request.json
    if not all(data.get(k) for k in ["email", "password", "college"]):
        return jsonify({"error": "Please fill all information"}), 400
    if len(data.get("password")) < 8:
        return jsonify({"error": "Stronger password. Please"}), 400
    u_id = str(uuid.uuid1())
    try:
        login_utils.add_new_invite(u_id=u_id, **data)
        send_email_in_background(email_client.prepare_invite, data.get("email"), u_id)
    except Exception as e:
        print(e)
        return jsonify({"error": "Signup request already sent. Do not SPAM"}), 400
    return jsonify({"message": "Request submitted successfully"})


@app.route("/verify_user")
def verify_user():
    if "username" in session:
        return redirect("/")
    u_id = request.args.get("u_id")
    if not u_id:
        return jsonify({"error": "Missing or invalid u_id"}), 400
    try:
        login_utils.accept_invite(u_id)
    except ValueError:
        return jsonify({"error": "Unable to process request"}), 400
    return render_template("invite_success.html")


@app.route("/login", methods=["POST"])
def login_p():
    if "username" in session:
        return redirect("/")
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        if login_client.login_verify(username, password):
            session.clear()
            session["username"] = username
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/login_page/")
def login_page():
    if "username" in session:
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login_page/")


@app.route("/")
def test_upload():
    return render_template("upload.html", project_name=CONFIG.APP_NAME)

@app.route("/dashboard", methods=["POST"])
def dd():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file"}), 400
    filename = secure_filename(file.filename)
    pf_path = os_path.join(CONFIG.UPLOAD_FOLDER, filename)
    file.save(pf_path)
    ws_out_fold = os_path.join(CONFIG.UPLOAD_FOLDER, f"output_{file.filename}_{randint(10000, 999999)}")
    makedirs(ws_out_fold, exist_ok=True)
    pdf_parser = PDFParser(pf_path)
    text = pdf_parser.extract_text()
    college_code = request.form.get("college_code")
    college_code = college_code.strip() if college_code else None
    text_parser = TextParser(text, save_folder=ws_out_fold, college_code=college_code)
    f_path = text_parser.extract_data_and_return_as_csv()
    session['f_path'] = f_path
    a, b_data = text_parser.text_matcher_year_wise()
    with open("new.json", "w") as f:
        json.dump(b_data, f, indent=4)
    return render_template('dashboard.html', analysis_data=a, subject_code_and_name=text_parser.subj_CODE)


@app.route("/download_stream_csv/<stream_name>", methods=["GET"])
def download_stream_csv(stream_name):
    ws_out_fold = session.get('f_path')
    if not ws_out_fold or not os_path.exists(ws_out_fold):
        return jsonify({"error": "No data available. Please upload a PDF first."}), 404
    csv_filename = f"{stream_name}_results.xlsx"
    csv_path = os_path.join(ws_out_fold, csv_filename)
    
    if not os_path.exists(csv_path):
        return jsonify({"error": f"CSV file for stream {stream_name} not found"}), 404
    return send_file(
        csv_path,
        as_attachment=True,
        download_name=f"{stream_name}_data.xlsx",
    )