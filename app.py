from flask import Flask, request, redirect, session, url_for, jsonify
import requests
from requests.auth import HTTPBasicAuth
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key')

# Конфигурация Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://robot-dyak-archive-1.onrender.com/callback"  # <-- ЗАМЕНИ НА СВОЙ URL, КОГДА УЗНАЕШЬ
SCOPES = 'https://www.googleapis.com/auth/drive.file'

@app.route('/')
def home():
    if 'google_token' in session:
        return '<h1>Шлюз Google Drive активен</h1><p>Токен получен. Можно работать с Диском.</p>'
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}&access_type=offline"
    return f'<a href="{auth_url}">Авторизовать доступ к Google Drive</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data)
    tokens = response.json()
    session['google_token'] = tokens.get('access_token')
    session['refresh_token'] = tokens.get('refresh_token')
    return redirect(url_for('home'))

@app.route('/test')
def test():
    if 'google_token' not in session:
        return redirect(url_for('home'))
    # Простой тест: получить информацию о пользователе Диска
    headers = {'Authorization': f"Bearer {session['google_token']}"}
    drive_response = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', headers=headers)
    return f'<pre>{json.dumps(drive_response.json(), indent=2)}</pre>'

if __name__ == '__main__':
    app.run(debug=True)
