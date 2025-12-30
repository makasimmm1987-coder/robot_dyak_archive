from flask import Flask, request, redirect, session, url_for, jsonify
import requests
import os
import json

# Инициализация приложения
app = Flask(__name__)

# ===================== КОНФИГУРАЦИЯ =====================
# Ключи берутся из переменных окружения Render
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key-change-in-production')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# КРИТИЧЕСКИ ВАЖНО: Проверь, что этот URL совпадает с твоим сервисом!
REDIRECT_URI = "https://robot-dyak-archive-1.onrender.com/callback"
SCOPES = 'https://www.googleapis.com/auth/drive.file'

# ===================== МАРШРУТЫ =====================
@app.route('/')
def home():
    """Главная страница шлюза"""
    # Если токен уже есть, показываем статус
    if 'google_token' in session:
        return '''
        <h1>✅ Шлюз Google Drive активен!</h1>
        <p>Токен доступа получен. Теперь можно работать с Диском.</p>
        <p><a href="/test">🔍 Проверить связь с Google Drive</a></p>
        <p><a href="/logout">🚪 Выйти</a></p>
        '''
    
    # Если токена нет, показываем кнопку авторизации
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}&access_type=offline"
    return f'''
    <h1>🚀 Добро пожаловать в шлюз архива!</h1>
    <p>Это твой персональный шлюз для работы с Google Drive API.</p>
    <p><a href="{auth_url}" style="font-size: 1.2em; padding: 10px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px;">🔑 Авторизовать доступ к Google Drive</a></p>
    <p><small>Будет выполнен вход в аккаунт: <strong>makasimmm.1987@gmail.com</strong></small></p>
    '''

@app.route('/callback')
def callback():
    """Обработчик перенаправления от Google после авторизации"""
    # Получаем код авторизации из URL
    auth_code = request.args.get('code')
    
    if not auth_code:
        return "Ошибка: код авторизации не получен", 400
    
    # Формируем запрос для обмена кода на токен
    token_data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        # Отправляем запрос к Google для получения токенов
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_response.raise_for_status()  # Проверяем на ошибки HTTP
        
        tokens = token_response.json()
        
        # Сохраняем токены в сессии
        session['google_token'] = tokens.get('access_token')
        session['refresh_token'] = tokens.get('refresh_token')
        
        # Перенаправляем на главную страницу
        return redirect(url_for('home'))
        
    except requests.exceptions.RequestException as e:
        return f"Ошибка при получении токена: {str(e)}", 500

@app.route('/test')
def test():
    """Тестовая страница для проверки связи с Google Drive"""
    # Проверяем, есть ли токен в сессии
    if 'google_token' not in session:
        return redirect(url_for('home'))
    
    # Пробуем получить информацию о пользователе
    headers = {'Authorization': f'Bearer {session["google_token"]}'}
    
    try:
        response = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        
        # Форматируем вывод
        return f'''
        <h2>🎉 Связь с Google Drive установлена!</h2>
        <p>Твой аккаунт: <strong>{user_data.get('user', {}).get('emailAddress', 'Неизвестно')}</strong></p>
        <details>
            <summary>📊 Полный ответ от Google Drive API:</summary>
            <pre>{json.dumps(user_data, indent=2, ensure_ascii=False)}</pre>
        </details>
        <p><a href="/">🏠 На главную</a> | <a href="/logout">🚪 Выйти</a></p>
        '''
        
    except requests.exceptions.RequestException as e:
        return f'''
        <h2>❌ Ошибка при запросе к Drive</h2>
        <p><strong>Детали:</strong> {str(e)}</p>
        <p>Возможно, срок действия токена истёк. Попробуй <a href="/logout">выйти</a> и авторизоваться заново.</p>
        <p><a href="/">🏠 На главную</a></p>
        '''

@app.route('/logout')
def logout():
    """Выход из системы (очистка сессии)"""
    session.clear()
    return '''
    <h2>👋 Сессия завершена</h2>
    <p>Ты вышел из системы. Токены доступа были удалены.</p>
    <p><a href="/">🔑 Авторизоваться заново</a></p>
    '''

# ===================== ЗАПУСК =====================
if __name__ == '__main__':
    # Локальный запуск (на Render эта часть не выполняется)
    app.run(debug=True, host='0.0.0.0', port=5000)
