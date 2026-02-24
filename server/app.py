from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import ssl
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

scores = []

GAME_COMPUTER_URL = "http://192.168.10.30:8080/update_leaderboard"

def get_top_10():
    sorted_scores = sorted(scores, key=lambda x: (-x['score'], x['timestamp']))
    return [
        {
            'user': s['user'],
            'score': s['score'],
            'timestamp': s['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in sorted_scores[:10]
    ]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/submit_score', methods=['POST'])
def submit_score():
    data=request.get_json()
    if not data or "user" not in data or "score" not in data:
        return jsonify({"error": "Invalid data"}),400
    scores.append({
        'user':data['user'],
        'score':int(data['score']),
        'timestamp':datetime.now()
    })
    top_10=get_top_10()
    socketio.emit('update_leaderboard', top_10)
    try:
        requests.post(GAME_COMPUTER_URL, json={"leaderboard":top_10}, timeout=3)
    except Exception as e:
        print("Game computer unreachable:",e)
    return jsonify({"message":"Score submitted","top_10":top_10})

@socketio.on("connect")
def on_connect():
    emit("update_leaderboard", get_top_10())

import webbrowser
import threading

if __name__=="__main__":
    def open_browser():
        webbrowser.open_new("http://localhost:5000")

    # Start a timer to open the browser shortly after the server starts
    threading.Timer(1.0, open_browser).start()

    cert_path="cert.pem"
    key_path="key.pem"
    if os.path.exists(cert_path) and os.path.exists(key_path):
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(cert_path, key_path)
            print("Running with SSL")
            socketio.run(app, host="0.0.0.0", port=5000, ssl_context=ssl_context)
        except Exception as e:
            print(f"Error loading SSL cert/key: {e}")
            print("Running without SSL due to error")
            socketio.run(app, host="0.0.0.0", port=5000)
    else:
        print("Running without SSL (cert.pem or key.pem missing)")
        socketio.run(app, host="0.0.0.0", port=5000)

