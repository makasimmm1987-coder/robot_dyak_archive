from flask import Flask, request, redirect, session, url_for
import requests
import os
import json

# ================== НАСТРОЙКА ПРИЛОЖЕНИЯ ==================
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key-change-me')

# Ключи из переменных окружения Render
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# 🔗 КРИТИЧЕСКИ ВАЖНО: Этот адрес должен совпадать с настройками Google Cloud!
REDIRECT_URI = "https://robot-dyak-archive-1.onrender.com/callback"
SCOPES = 'https://www.googleapis.com/auth/drive.file'

# ================== ГЛАВНАЯ СТРАНИЦА ==================
@app.route('/')
def home():
    """Показываем кнопку авторизации или статус, если уже вошли."""
    if 'google_token' in session:
        return '''
        <h1>✅ Шлюз Google Drive активен!</h1>
        <p>Токен доступа получен. Теперь можно работать с Диском.</p>
        <p><a href="/test">🔍 Проверить связь с Google Drive</a></p>
        <p><a href="/logout">🚪 Выйти</a></p>
        '''
    # Создаём URL для авторизации в Google
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}&access_type=offline"
    return f'''
    <h1>🚀 Добро пожаловать в шлюз архива!</h1>
    <p>Это твой персональный шлюз для работы с Google Drive API.</p>
    <p><a href="{auth_url}" style="font-size: 1.2em; padding: 10px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px;">🔑 Авторизовать доступ к Google Drive</a></p>
    <p><small>Будет выполнен вход в аккаунт: <strong>makasimmm.1987@gmail.com</strong></small></p>
    '''

# ================== ОБРАБОТЧИК ОТВЕТА ОТ GOOGLE ==================
@app.route('/callback')
def callback():
    """Google перенаправляет сюда после того, как пользователь дал разрешение."""
    auth_code = request.args.get('code')
    if not auth_code:
        return "Ошибка: код авторизации не получен.", 400

    # Меняем код на токен доступа
    token_data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    try:
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_response.raise_for_status()  # Проверяем ошибки HTTP
        tokens = token_response.json()

        # Сохраняем токены в сессии
        session['google_token'] = tokens.get('access_token')
        session['refresh_token'] = tokens.get('refresh_token')
        return redirect(url_for('home'))

    except requests.exceptions.RequestException as e:
        return f"Ошибка при получении токена: {str(e)}", 500

# ================== СТРАНИЦА ТЕСТИРОВАНИЯ СВЯЗИ ==================
@app.route('/test')
def test():
    """Проверяем, можем ли мы сделать запрос к Google Drive с нашим токеном."""
    if 'google_token' not in session:
        return redirect(url_for('home'))

    headers = {'Authorization': f'Bearer {session["google_token"]}'}
    try:
        response = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', headers=headers)
        response.raise_for_status()
        user_data = response.json()
        return f'''
        <h2>🎉 Связь с Google Drive установлена!</h2>
        <p>Твой аккаунт: <strong>{user_data.get('user', {}).get('emailAddress', 'Неизвестно')}</strong></p>
        <details>
            <summary>📊 Полный ответ от Google:</summary>
            <pre>{json.dumps(user_data, indent=2, ensure_ascii=False)}</pre>
        </details>
        <p><a href="/">🏠 На главную</a> | <a href="/logout">🚪 Выйти</a></p>
        '''
    except requests.exceptions.RequestException as e:
        return f'''
        <h2>❌ Ошибка при запросе к Drive</h2>
        <p><strong>Детали:</strong> {str(e)}</p>
        <p>Попробуй <a href="/logout">выйти</a> и авторизоваться заново.</p>
        <p><a href="/">🏠 На главную</a></p>
        '''

# ================== ВЫХОД ИЗ СИСТЕМЫ ==================
@app.route('/logout')
def logout():
    """Очищаем сессию и выходим."""
    session.clear()
    return '''
    <h2>👋 Сессия завершена</h2>
    <p>Ты вышел из системы. Токены удалены.</p>
    <p><a href="/">🔑 Авторизоваться заново</a></p>
    '''

# ================== ЗАПУСК (для локальной разработки) ==================
if __name__ == '__main__':
    app.run(debug=True)
