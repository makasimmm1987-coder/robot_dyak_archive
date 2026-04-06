from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = " 5378117961"  # пока оставь так, потом заменим

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    cmd = data.get('cmd', '')
    if not cmd:
        return jsonify({"error": "cmd required"}), 400
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": cmd}
    r = requests.post(url, json=payload)
    
    return jsonify({"status": "sent", "command": cmd, "telegram_response": r.json()})

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"})
