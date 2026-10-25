import os
import json
import base64
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("TUNEBASE_SECRET_KEY", "change-this-for-local-development")

# Connects to the EXISTING TuneBase database. It does not create or reset tables.
DB_CONFIG = {
    "host": os.getenv("TUNEBASE_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("TUNEBASE_DB_PORT", "3306")),
    "user": os.getenv("TUNEBASE_DB_USER", "root"),
    "password": os.getenv("TUNEBASE_DB_PASSWORD", ""),
    "database": os.getenv("TUNEBASE_DB_NAME", "TuneBase"),
}

# This metadata matches the uploaded MySQL schema.sql.
# pk is a tuple because Playlist_Songs and Likes use composite primary keys.
TABLES = {
    "Users": {
        "pk": ("user_id",), "label": "username",
        "fields": [
            ("username", "Username", "text", None),
            ("email", "Email", "email", None),
            ("password_hash", "Password", "password", None),
        ],
        "columns": ["user_id", "username", "email", "join_date"],
    },
    "Artists": {
        "pk": ("artist_id",), "label": "artist_name",
        "fields": [
            ("artist_name", "Artist name", "text", None),
            ("country", "Country", "text", None),
        ],
        "columns": ["artist_id", "artist_name", "country"],
    },
    "Albums": {
        "pk": ("album_id",), "label": "album_title",
        "fields": [
            ("album_title", "Album title", "text", None),
            ("release_date", "Release date", "date", None),
            ("artist_id", "Artist", "fk", "Artists"),
        ],
        "columns": ["album_id", "album_title", "release_date", "artist_id"],
    },
    "Songs": {
        "pk": ("song_id",), "label": "song_title",
        "fields": [
            ("song_title", "Song title", "text", None),
            ("duration_seconds", "Duration (seconds)", "number", None),
            ("genre", "Genre", "text", None),
            ("album_id", "Album", "fk", "Albums"),
        ],
        "columns": ["song_id", "song_title", "duration_seconds", "genre", "album_id"],
    },
    "Playlists": {
        "pk": ("playlist_id",), "label": "playlist_name",
        "fields": [
            ("playlist_name", "Playlist name", "text", None),
            ("user_id", "Owner", "fk", "Users"),
        ],
        "columns": ["playlist_id", "playlist_name", "user_id", "created_at"],
    },
    "Playlist_Songs": {
        "pk": ("playlist_id", "song_id"), "label": None,
        "fields": [
            ("playlist_id", "Playlist", "fk", "Playlists"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": ["playlist_id", "song_id", "added_at"],
    },
    "Likes": {
        "pk": ("user_id", "song_id"), "label": None,
        "fields": [
            ("user_id", "User", "fk", "Users"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": ["user_id", "song_id", "liked_at"],
    },
    "Listening_History": {
        "pk": ("history_id",), "label": None,
        "fields": [
            ("user_id", "User", "fk", "Users"),
            ("song_id", "Song", "fk", "Songs"),
        ],
        "columns": ["history_id", "user_id", "song_id", "played_at"],
    },
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def key_encode(row, pk):
    values = [str(row[col]) for col in pk]
    raw = json.dumps(values).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def key_decode(token, pk):
    token += "=" * (-len(token) % 4)
    values = json.loads(base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8"))
    if not isinstance(values, list) or len(values) != len(pk):
        raise ValueError("Invalid record key.")
    return values

def display_value(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.isoformat()
    return value

@app.context_processor
def inject_globals():
    return {"table_names": list(TABLES.keys())}

@app.route("/")
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

@app.route("/table/<table_name>", methods=["GET", "POST"])
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

        # Save or delete a record.
        if request.method == "POST":
            action = request.form.get("action", "save")
            token = request.form.get("key", "")
            if action == "delete":
                values = key_decode(token, pk)
                where = " AND ".join(f"`{col}`=%s" for col in pk)
                cur.execute(f"DELETE FROM `{table_name}` WHERE {where}", values)
                conn.commit()
                flash("Record deleted.", "ok")
                return redirect(url_for("table_view", table_name=table_name))

            values = []
            for col, label, kind, fk in fields:
                raw = request.form.get(col, "").strip()
                if kind == "password":
                    # Never store the example password as plaintext.
                    if raw:
                        values.append(generate_password_hash(raw))
                    elif token:
                        values.append(None)  # preserve existing hash below
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
                if table_name == "Users" and not request.form.get("password_hash", "").strip():
                    cur.execute("SELECT password_hash FROM Users WHERE user_id=%s", old_key)
                    old = cur.fetchone()
                    if old:
                        values[field_names.index("password_hash")] = old["password_hash"]
                assignments = ", ".join(f"`{col}`=%s" for col in field_names)
                where = " AND ".join(f"`{col}`=%s" for col in pk)
                cur.execute(
                    f"UPDATE `{table_name}` SET {assignments} WHERE {where}",
                    values + old_key
                )
            else:
                cols = ", ".join(f"`{col}`" for col in field_names)
                placeholders = ", ".join(["%s"] * len(field_names))
                cur.execute(
                    f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})",
                    values
                )
            conn.commit()
            flash("Record saved successfully.", "ok")
            return redirect(url_for("table_view", table_name=table_name))

        # Foreign-key dropdown options.
        for col, label, kind, fk in fields:
            if kind == "fk":
                fk_cfg = TABLES[fk]
                fk_cur = conn.cursor(dictionary=True)
                fk_cur.execute(
                    f"SELECT `{fk_cfg['pk'][0]}` AS id, "
                    f"`{fk_cfg['label']}` AS name FROM `{fk}` ORDER BY name"
                    if fk_cfg["label"] else
                    f"SELECT `{fk_cfg['pk'][0]}` AS id, "
                    f"CONCAT_WS(' / ', {', '.join('`'+x+'`' for x in fk_cfg['pk'])}) AS name "
                    f"FROM `{fk}` ORDER BY id"
                )
                opts[col] = fk_cur.fetchall()
                fk_cur.close()

        if edit_token:
            edit_values = key_decode(edit_token, pk)
            where = " AND ".join(f"`{col}`=%s" for col in pk)
            cur.execute(f"SELECT * FROM `{table_name}` WHERE {where}", edit_values)
            edit = cur.fetchone()

        select_cols = ", ".join(f"`{col}`" for col in cfg["columns"])
        sql = f"SELECT {select_cols} FROM `{table_name}`"
        args = []
        if q:
            searchable = [f[0] for f in fields if f[2] != "password"]
            if searchable:
                sql += " WHERE " + " OR ".join(f"CAST(`{col}` AS CHAR) LIKE %s" for col in searchable)
                args = [f"%{q}%"] * len(searchable)
        sql += " ORDER BY " + ", ".join(f"`{col}` DESC" for col in pk)
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

    # Make row values JSON-safe and attach an opaque key for edit/delete links.
    prepared = []
    for row in rows:
        item = {k: display_value(v) for k, v in row.items()}
        item["_key"] = key_encode(row, pk)
        prepared.append(item)

    edit_key = key_encode(edit, pk) if edit else ""
    return render_template(
        "index.html", page="table", current_table=table_name, cfg=cfg,
        rows=prepared, opts=opts, edit=edit, edit_key=edit_key, q=q
    )

if __name__ == "__main__":
    app.run(debug=True)
