
import os
import json
import base64
import re
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
import mysql.connector
from mysql.connector import Error
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

app.secret_key = os.getenv(
    "TUNEBASE_SECRET_KEY",
    "change-this-for-local-development"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("TUNEBASE_HTTPS", "0") == "1",
    PERMANENT_SESSION_LIFETIME=43200
)

csrf = CSRFProtect(app)


# DATABASE CONNECTION

DB_CONFIG = {
    "host": os.getenv("TUNEBASE_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("TUNEBASE_DB_PORT", "3306")),
    "user": os.getenv("TUNEBASE_DB_USER", "root"),
    "password": os.getenv("TUNEBASE_DB_PASSWORD", ""),
    "database": os.getenv("TUNEBASE_DB_NAME", "TuneBase"),
}


# DATABASE TABLE CONFIGURATION

TABLES = {
    "Users": {
        "pk": ("user_id",),
        "label": "username",
        "fields": [
            ("first_name", "First name", "text", None),
            ("last_name", "Last name", "text", None),
            ("username", "Username", "text", None),
            ("email", "Email", "email", None),
            ("password_hash", "Password", "password", None),
            ("date_of_birth", "Date of birth", "date", None),
        ],
        "columns": [
            "user_id", "first_name", "last_name",
            "username", "email", "join_date", "date_of_birth"
        ],
    },

    "Artists": {
        "pk": ("artist_id",),
        "label": "artist_name",
        "fields": [
            ("artist_name", "Artist name", "text", None),
            ("country", "Country", "text", None),
        ],
        "columns": ["artist_id", "artist_name", "country"],
    },

    "Albums": {
        "pk": ("album_id",),
        "label": "album_title",
        "fields": [
            ("album_title", "Album title", "text", None),
            ("release_date", "Release date", "date", None),
            ("artist_id", "Artist", "fk", "Artists"),
        ],
        "columns": [
            "album_id", "album_title", "release_date", "artist_id"
        ],
    },

    "Songs": {
        "pk": ("song_id",),
        "label": "song_title",
        "fields": [
            ("song_title", "Song title", "text", None),
            ("duration_seconds", "Duration (seconds)", "number", None),
            ("genre", "Genre", "text", None),
            ("album_id", "Album", "fk", "Albums"),
        ],
        "columns": [
            "song_id", "song_title", "duration_seconds",
            "genre", "album_id"
        ],
    },

    "Playlists": {
        "pk": ("playlist_id",),
        "label": "playlist_name",
        "fields": [
            ("playlist_name", "Playlist name", "text", None),
            ("user_id", "Owner", "fk", "Users"),
        ],
        "columns": [
            "playlist_id", "playlist_name", "user_id", "created_at"
        ],
    },

    "Playlist_Songs": {
        "pk": ("playlist_id", "song_id"),
        "label": None,
        "fields": [
            ("playlist_id", "Playlist", "fk", "Playlists"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": ["playlist_id", "song_id", "added_at"],
    },

    "Likes": {
        "pk": ("user_id", "song_id"),
        "label": None,
        "fields": [
            ("user_id", "User", "fk", "Users"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": ["user_id", "song_id", "liked_at"],
    },

    "Listening_History": {
        "pk": ("history_id",),
        "label": None,
        "fields": [
            ("user_id", "User", "fk", "Users"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": [
            "history_id", "user_id", "song_id", "played_at"
        ],
    },

    "User_Phone_Numbers": {
        "pk": ("phone_id",),
        "label": "phone_number",
        "fields": [
            ("user_id", "User", "fk", "Users"),
            ("phone_number", "Phone number", "text", None),
        ],
        "columns": ["phone_id", "user_id", "phone_number"],
    },
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# AUTHENTICATION DECORATOR

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access TuneBase.", "err")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


# HELPER FUNCTIONS

def key_encode(row, pk):
    values = [str(row[col]) for col in pk]
    raw = json.dumps(values).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def key_decode(token, pk):
    token += "=" * (-len(token) % 4)
    values = json.loads(
        base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    )
    if not isinstance(values, list) or len(values) != len(pk):
        raise ValueError("Invalid record key.")
    return values


def display_value(value):
    if isinstance(value, (date, datetime)):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.isoformat()
    return value

def verify_password(stored_hash, password):
    try:
        return check_password_hash(stored_hash, password)
    except (ValueError, TypeError):
        return False

@app.context_processor
def inject_globals():
    return {
        "table_names": list(TABLES.keys()),
        "current_user": {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "first_name": session.get("first_name")
        } if "user_id" in session else None
    }


# LOGIN PAGE

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Enter your username/email and password.", "err")
            return render_template("login.html")

        conn = None

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute("""
                SELECT user_id, username, first_name, password_hash
                FROM Users
                WHERE username = %s OR email = %s
            """, (identifier, identifier))

            user = cur.fetchone()
            cur.close()

            if user and verify_password(
                user["password_hash"], password
            ):
                session.clear()
                session.permanent = True
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["first_name"] = user["first_name"] or user["username"]

                flash("Welcome back to TuneBase!", "ok")
                return redirect(url_for("home"))

            flash("Invalid username/email or password.", "err")

        except Error as exc:
            flash(f"Database error: {exc}", "err")

        finally:
            if conn and conn.is_connected():
                conn.close()

    return render_template("login.html")


# REGISTRATION PAGE

@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        dob = request.form.get("date_of_birth", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        phone_input = request.form.get("phone_numbers", "").strip()

        if not all([
            first_name, last_name, username,
            email, dob, password, confirm_password
        ]):
            flash("Please fill in all required fields.", "err")
            return render_template("register.html")

        if len(username) > 50 or len(email) > 100:
            flash("Username or email is too long.", "err")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "err")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "err")
            return render_template("register.html")

        try:
            birth_date = date.fromisoformat(dob)

            if birth_date >= date.today():
                raise ValueError

        except ValueError:
            flash("Please enter a valid date of birth.", "err")
            return render_template("register.html")

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "err")
            return render_template("register.html")

        phones = [
            p.strip() for p in phone_input.split(",") if p.strip()
        ]

        if len(phones) != len(set(phones)):
            flash("Duplicate phone numbers are not allowed.", "err")
            return render_template("register.html")

        if any(
            not re.fullmatch(r"[0-9+\-\s()]{7,20}", p)
            for p in phones
        ):
            flash("Please enter valid phone numbers.", "err")
            return render_template("register.html")

        conn = None

        try:
            conn = get_connection()
            cur = conn.cursor()

            password_hash = generate_password_hash(password)

            cur.execute("""
                INSERT INTO Users
                (first_name, last_name, username, email,
                 password_hash, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                first_name, last_name, username, email,
                password_hash, birth_date
            ))

            new_user_id = cur.lastrowid

            for phone in phones:
                cur.execute("""
                    INSERT INTO User_Phone_Numbers
                    (user_id, phone_number)
                    VALUES (%s, %s)
                """, (new_user_id, phone))

            conn.commit()
            cur.close()

            flash("Registration successful! Please log in.", "ok")
            return redirect(url_for("login"))

        except Error as exc:
            if conn:
                conn.rollback()

            if exc.errno == 1062:
                flash("Username or email already exists.", "err")
            else:
                flash(f"Registration failed: {exc}", "err")

        finally:
            if conn and conn.is_connected():
                conn.close()

    return render_template("register.html")


# LOGOUT

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "ok")
    return redirect(url_for("login"))


# HOME DASHBOARD

@app.route("/")
@login_required
def home():

    counts = {}
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        for table in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM `{table}`")
            counts[table] = cur.fetchone()[0]

        cur.close()

    except Error as exc:
        flash(f"Could not connect to MySQL: {exc}", "err")

    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("index.html", page="home", counts=counts)


# GENERIC CRUD OPERATIONS

@app.route("/table/<table_name>", methods=["GET", "POST"])
@login_required
def table_view(table_name):

    if table_name not in TABLES:
        flash("Unknown table.", "err")
        return redirect(url_for("home"))

    cfg = TABLES[table_name]
    pk = cfg["pk"]
    fields = cfg["fields"]
    field_names = [f[0] for f in fields]

    conn = None
    opts = {}
    rows = []
    edit = None
    q = request.args.get("q", "").strip()
    edit_token = request.args.get("edit")
    edit_values = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        if request.method == "POST":

            action = request.form.get("action", "save")
            token = request.form.get("key", "")

            if action == "delete":

                values = key_decode(token, pk)
                where = " AND ".join(
                    f"`{col}`=%s" for col in pk
                )

                cur.execute(
                    f"DELETE FROM `{table_name}` WHERE {where}",
                    values
                )

                conn.commit()
                flash("Record deleted.", "ok")
                return redirect(url_for(
                    "table_view", table_name=table_name
                ))

            values = []

            for col, label, kind, fk in fields:

                raw = request.form.get(col, "").strip()

                if kind == "password":

                    if raw:
                        values.append(generate_password_hash(raw))
                    elif token:
                        values.append(None)
                    else:
                        values.append(generate_password_hash(""))

                elif raw == "":
                    values.append(None)

                elif kind == "number":
                    values.append(int(raw))

                else:
                    values.append(raw)

            if token:

                old_key = key_decode(token, pk)

                if table_name == "Users":
                    if not request.form.get(
                        "password_hash", ""
                    ).strip():

                        cur.execute(
                            "SELECT password_hash FROM Users WHERE user_id=%s",
                            old_key
                        )

                        old = cur.fetchone()

                        if old:
                            values[
                                field_names.index("password_hash")
                            ] = old["password_hash"]

                assignments = ", ".join(
                    f"`{col}`=%s" for col in field_names
                )

                where = " AND ".join(
                    f"`{col}`=%s" for col in pk
                )

                cur.execute(
                    f"UPDATE `{table_name}` SET {assignments} WHERE {where}",
                    values + old_key
                )

            else:

                cols = ", ".join(
                    f"`{col}`" for col in field_names
                )

                placeholders = ", ".join(
                    ["%s"] * len(field_names)
                )

                cur.execute(
                    f"INSERT INTO `{table_name}` ({cols}) "
                    f"VALUES ({placeholders})",
                    values
                )

            conn.commit()
            flash("Record saved successfully.", "ok")

            return redirect(url_for(
                "table_view", table_name=table_name
            ))

        # FOREIGN KEY DROPDOWNS

        for col, label, kind, fk in fields:

            if kind == "fk":

                fk_cfg = TABLES[fk]
                fk_cur = conn.cursor(dictionary=True)

                if fk_cfg["label"]:

                    fk_cur.execute(
                        f"SELECT `{fk_cfg['pk'][0]}` AS id, "
                        f"`{fk_cfg['label']}` AS name "
                        f"FROM `{fk}` ORDER BY name"
                    )

                else:

                    fk_cur.execute(
                        f"SELECT `{fk_cfg['pk'][0]}` AS id, "
                        f"CONCAT_WS(' / ', "
                        f"{', '.join('`'+x+'`' for x in fk_cfg['pk'])}) "
                        f"AS name FROM `{fk}` ORDER BY id"
                    )

                opts[col] = fk_cur.fetchall()
                fk_cur.close()

        # EDIT RECORD

        if edit_token:

            edit_values = key_decode(edit_token, pk)

            where = " AND ".join(
                f"`{col}`=%s" for col in pk
            )

            cur.execute(
                f"SELECT * FROM `{table_name}` WHERE {where}",
                edit_values
            )

            edit = cur.fetchone()

        # SEARCH AND DISPLAY

        select_cols = ", ".join(
            f"`{col}`" for col in cfg["columns"]
        )

        sql = f"SELECT {select_cols} FROM `{table_name}`"
        args = []

        if q:

            searchable = [
                f[0] for f in fields if f[2] != "password"
            ]

            if searchable:

                sql += " WHERE " + " OR ".join(
                    f"CAST(`{col}` AS CHAR) LIKE %s"
                    for col in searchable
                )

                args = [f"%{q}%"] * len(searchable)

        sql += " ORDER BY " + ", ".join(
            f"`{col}` DESC" for col in pk
        )

        cur.execute(sql, args)
        rows = cur.fetchall()
        cur.close()

    except (Error, ValueError, KeyError, json.JSONDecodeError) as exc:

        if conn:
            conn.rollback()

        flash(f"Operation failed: {exc}", "err")

    finally:

        if conn and conn.is_connected():
            conn.close()

    prepared = []

    for row in rows:

        item = {
            k: display_value(v) for k, v in row.items()
        }

        item["_key"] = key_encode(row, pk)
        prepared.append(item)

    edit_key = key_encode(edit, pk) if edit else ""

    return render_template(
        "index.html",
        page="table",
        current_table=table_name,
        cfg=cfg,
        rows=prepared,
        opts=opts,
        edit=edit,
        edit_key=edit_key,
        q=q
    )


if __name__ == "__main__":
    app.run(debug=True)
