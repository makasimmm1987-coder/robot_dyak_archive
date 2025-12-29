from flask import Flask, request, redirect, session, url_for, jsonify
import requests
from requests.auth import HTTPBasicAuth
import json
import os

app = Flask(__name__)
# Секретный ключ берётся из переменной окружения, которую мы уже добавили
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Конфигурация Google OAuth (берётся из переменных окружения)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
# 🔗 ОБЯЗАТЕЛЬНО проверь, что этот URL совпадает с твоим сервисом!
REDIRECT_URI = "https://robot-dyak-archive-1.onrender.com/callback"
SCOPES = 'https://www.googleapis.com/auth/drive.file'

@app.route('/')
def home():
    if 'google_token' in session:
        return '<h1>Шлюз Google Drive активен!</h1><p>Токен получен. Можно тестировать работу с Диском.</p><p><a href="/test">Проверить связь с Google Drive</a></p>'
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}&access_type=offline"
    return f'<h1>Добро пожаловать в шлюз архива!</h1><p><a href="{auth_url}">🔑 Авторизовать доступ к Google Drive</a></p>'

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
    # Сохраняем токены в сессии
    session['google_token'] = tokens.get('access_token')
    session['refresh_token'] = tokens.get('refresh_token')  # Важно для продления доступа
    return redirect(url_for('home'))

@app.route('/test')
def test():
    if 'google_token' not in session:
        return redirect(url_for('home'))
    # Простой тест: получаем информацию о пользователе Диска
    headers = {'Authorization': f"Bearer {session['google_token']}"}
    try:
        drive_response = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', headers=headers)
        user_info = drive_response.json()
        return f'<h2>Связь с Google Drive установлена!</h2><pre>{json.dumps(user_info, indent=2)}</pre><p><a href="/">На главную</a></p>'
    except Exception as e:
        return f'<h2>Ошибка при запросе к Drive</h2><p>{e}</p>'

if __name__ == '__main__':
    app.run(debug=True)
