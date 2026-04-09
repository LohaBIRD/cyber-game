import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv
import psycopg2

# ✅ Load environment variables FIRST
load_dotenv()

DATABASE_URL = os.getenv("postgresql://neondb_owner:npg_6iORorEfVZ0N@ep-winter-king-abm8qnkd-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your environment variables.")

# ✅ Flask setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ Database connection helper
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

# ✅ Ensure table exists (runs on startup)
def init_db():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized")
    except Exception as e:
        print("❌ Error initializing DB:", e)

init_db()

# 🎮 Root route (health check)
@app.route("/")
def home():
    return "Leaderboard API is running 🚀"

# 📥 Submit score
@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("user")
    score = data.get("score")

    if username is None or score is None:
        return jsonify({"error": "Missing user or score"}), 400

    print(f"📥 Received score: {username} -> {score}")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scores (username, score) VALUES (%s, %s)",
            (username, score)
        )
        conn.commit()
        cur.close()
        conn.close()

        # 🔔 Emit leaderboard update
        socketio.emit("new_score", {"user": username, "score": score})

        return jsonify({"message": "Score submitted successfully"}), 200

    except Exception as e:
        print("❌ Error inserting score:", e)
        return jsonify({"error": "Failed to insert score"}), 500

# 📊 Get leaderboard
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT username, score
            FROM scores
            ORDER BY score DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        leaderboard_data = [
            {"user": row[0], "score": row[1]}
            for row in rows
        ]

        return jsonify(leaderboard_data), 200

    except Exception as e:
        print("❌ Error fetching leaderboard:", e)
        return jsonify({"error": "Failed to fetch leaderboard"}), 500

# 🚀 Run app (for local dev only)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

