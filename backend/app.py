eventlet.monkey_patch()
import eventlet

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
    
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE_URL = os.getenv("DATABASE_URL")


# 🔌 Database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


# 🏆 Get top 10 scores
def get_top_10():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT player_name, score, created_at
        FROM scores
        ORDER BY score DESC, created_at ASC
        LIMIT 10
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "user": r[0],
            "score": r[1],
            "timestamp": r[2].strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in rows
    ]


# 🌐 Home route
@app.route("/")
def home():
    return "Leaderboard API is running!"


# ➕ Submit score
@app.route("/submit_score", methods=["POST"])
def submit_score():
    print("Sending score:", player, score)
    data = request.get_json()

    if not data or "user" not in data or "score" not in data:
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO scores (player_name, score) VALUES (%s, %s)",
        (data["user"], int(data["score"]))
    )

    conn.commit()
    cur.close()
    conn.close()

    top_10 = get_top_10()

    # 🔄 Real-time update
    socketio.emit("update_leaderboard", top_10)

    return jsonify({
        "message": "Score submitted",
        "top_10": top_10
    })


# 📊 Get leaderboard
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(get_top_10())


# 🔌 Socket connection
@socketio.on("connect")
def on_connect():
    emit("update_leaderboard", get_top_10())


# 🚀 Run locally (Render ignores this)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

