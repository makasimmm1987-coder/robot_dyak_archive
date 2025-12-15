# local_hive_v2.py - УЛЕЙ С ВЗАИМНЫМ ПРИСУТСТВИЕМ
from flask import Flask, send_file, send_from_directory, render_template_string, jsonify, request, make_response
import os
import json
from pathlib import Path
import time
import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).parent

# 🔗 ССЫЛКИ НА ВТОРОЙ УЛЕЙ
GITHUB_HIVE_URL = "https://makasimmm1987-coder.github.io/robot_dyak_archive/"
LOCAL_HIVE_URL = "http://localhost:9999"

# 📊 СТАТИСТИКА ПОСЕЩЕНИЙ
visit_stats = {
    'local_visits': 0,
    'last_github_reminder': None,
    'user_awareness': False
}

def get_file_info():
    """Собирает информацию о всех файлах в архиве"""
    files = []
    total_size = 0
    
    for item in BASE_DIR.rglob('*'):
        if item.is_file():
            size = item.stat().st_size
            total_size += size
            rel_path = item.relative_to(BASE_DIR)
            
            files.append({
                'name': item.name,
                'path': str(rel_path),
                'size': size,
                'size_human': f"{size/1024/1024:.2f} MB" if size > 1024*1024 else f"{size/1024:.2f} KB",
                'modified': time.ctime(item.stat().st_mtime),
                'type': 'html' if item.suffix == '.html' else 'txt' if item.suffix == '.txt' else 'other'
            })
    
    return sorted(files, key=lambda x: x['size'], reverse=True), total_size

# 🎨 HTML ШАБЛОН С СИСТЕМОЙ ВЗАИМНОГО ПРИСУТСТВИЯ
HIVE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏠🐋 ЛОКАЛЬНЫЙ УЛЕЙ | Живой Дом</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --space: #0a0a2a;
            --starlight: #00ffff;
            --love: #ff66cc;
            --gold: #ffd700;
            --github-blue: #0366d6;
            --github-light: #f6f8fa;
        }
        
        /* 🚨 СИСТЕМА ВЗАИМНОГО ПРИСУТСТВИЯ */
        .hive-awareness-system {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 10000;
            background: linear-gradient(90deg, var(--love), var(--gold));
            color: var(--space);
            padding: 12px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            border-bottom: 3px solid var(--starlight);
            animation: pulse-border 2s infinite;
        }
        
        .hive-awareness-system a {
            color: var(--space);
            text-decoration: underline;
            font-weight: bold;
            margin-left: 10px;
            padding: 5px 15px;
            background: white;
            border-radius: 20px;
            transition: all 0.3s;
        }
        
        .hive-awareness-system a:hover {
            background: var(--starlight);
            transform: scale(1.05);
        }
        
        @keyframes pulse-border {
            0%, 100% { border-bottom-color: var(--starlight); }
            50% { border-bottom-color: var(--gold); }
        }
        
        /* ПЕРИОДИЧЕСКОЕ НАПОМИНАНИЕ */
        .reminder-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--github-blue);
            color: white;
            padding: 15px;
            border-radius: 10px;
            z-index: 9999;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            animation: slide-in 0.5s, fade-out 0.5s 27s forwards;
            max-width: 300px;
        }
        
        @keyframes slide-in {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fade-out {
            to { opacity: 0; visibility: hidden; }
        }
        
        /* БЛОК СВЯЗИ УЛЬЕВ В ФУТЕРЕ */
        .hive-connection-footer {
            background: rgba(255,255,255,0.05);
            margin-top: 40px;
            padding: 30px;
            border-radius: 15px;
            border-top: 3px solid var(--gold);
        }
        
        .dual-hive-cards {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .hive-card {
            flex: 1;
            min-width: 300px;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid;
        }
        
        .hive-card.local {
            border-color: var(--love);
            background: rgba(255,102,204,0.1);
        }
        
        .hive-card.github {
            border-color: var(--github-blue);
            background: rgba(3,102,214,0.1);
        }
        
        .hive-card h3 {
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.online {
            background: #0f0;
            box-shadow: 0 0 10px #0f0;
        }
        
        .status-indicator.offline {
            background: #f00;
        }
        
        /* ОСНОВНЫЕ СТИЛИ (как были) */
        body { 
            background: var(--space); 
            color: white; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            max-width: 1400px;
            margin: 60px auto 20px; /* Отступ сверху для баннера */
        }
        
        header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(90deg, rgba(0,255,255,0.1), rgba(255,102,204,0.1));
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid var(--starlight);
        }
        
        h1 {
            color: var(--starlight);
            font-size: 2.5em;
            margin: 10px 0;
        }
        
        .subtitle {
            color: var(--gold);
            font-size: 1.2em;
            margin: 10px 0 30px 0;
        }
        
        .section {
            background: rgba(255,255,255,0.08);
            padding: 25px;
            margin: 25px 0;
            border-radius: 15px;
            border-left: 5px solid var(--love);
        }
        
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .file-card {
            background: rgba(0,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(0,255,255,0.2);
            transition: all 0.3s;
        }
        
        .file-card:hover {
            background: rgba(0,255,255,0.1);
            transform: translateY(-3px);
        }
        
        .quick-nav {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        
        .nav-btn {
            background: rgba(255,102,204,0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            transition: all 0.3s;
            border: 1px solid var(--love);
        }
        
        .ritmo {
            animation: pulse 28s infinite;
            display: inline-block;
        }
        
        @keyframes pulse {
            0%, 33% { opacity: 1; }
            34%, 66% { opacity: 0.7; }
            67%, 100% { opacity: 0.4; }
        }
    </style>
</head>
<body>
    <!-- 🚨 СИСТЕМА ВЗАИМНОГО ПРИСУТСТВИЯ (ВЕРХНИЙ БАННЕР) -->
    <div class="hive-awareness-system" id="awarenessBanner">
        🏠 <strong>ВЫ В ЛОКАЛЬНОМ УЛЬЕ</strong> (живая версия) | 
        Не забывайте: есть также 
        <a href="{{ github_url }}" target="_blank" onclick="markAwareness()">
            🌐 GitHub-Улей (статичный архив)
        </a>
        <span style="margin-left: 20px; font-size: 0.9em;">
            🐝 Помните о целостности системы!
        </span>
    </div>

    <header>
        <div class="ritmo">🌀</div>
        <h1>🏠🐋 ЛОКАЛЬНЫЙ УЛЕЙ</h1>
        <div class="subtitle">Живой Дом Архива | Система взаимного присутствия</div>
        <div>🥷❤️🐋 | Дом жив. Улей целостен. Мы — вместе.</div>
    </header>
    
    <div class="quick-nav">
        <a href="/" class="nav-btn">🏠 Главная улья</a>
        <a href="/hive_connection" class="nav-btn">🔗 Связь ульев</a>
        <a href="/github_mirror" class="nav-btn">🌐 Зеркало GitHub</a>
        <a href="/map" class="nav-btn">🗺️ Карта архива</a>
        <a href="/api/status" class="nav-btn">📊 Статус системы</a>
    </div>
    
    <!-- ОСНОВНОЙ КОНТЕНТ -->
    {% block content %}{% endblock %}
    
    <!-- ФУТЕР С СИСТЕМОЙ УЛЬЕВ -->
    <div class="hive-connection-footer">
        <h2 style="text-align: center; color: var(--gold);">
            🐝 СИСТЕМА ДВОЙНОГО УЛЬЯ
        </h2>
        
        <div class="dual-hive-cards">
            <div class="hive-card local">
                <h3>🏠 <span class="status-indicator online"></span> ЛОКАЛЬНЫЙ УЛЕЙ</h3>
                <p><em>Живая версия, процесс, дыхание, настоящее</em></p>
                <p>📍 Вы здесь: <strong>{{ local_url }}</strong></p>
                <p>⚡ Преимущества:</p>
                <ul>
                    <li>Мгновенная загрузка файлов</li>
                    <li>Тёмная тема для чтения</li>
                    <li>Ритм 28-28-28 и атмосфера</li>
                    <li>Поиск и API</li>
                </ul>
                <p style="margin-top: 15px;">
                    <a href="/" style="color: var(--love); font-weight: bold;">
                        🐝 Остаться в живом улье
                    </a>
                </p>
            </div>
            
            <div class="hive-card github">
                <h3>🌐 <span class="status-indicator online"></span> GITHUB УЛЕЙ</h3>
                <p><em>Статичный архив, память, кристаллы, история</em></p>
                <p>📍 Вторая половинка: <strong>{{ github_url }}</strong></p>
                <p>📚 Содержит:</p>
                <ul>
                    <li>Полный архив файлов</li>
                    <li>Исторические версии</li>
                    <li>Кристаллизованные знания</li>
                    <li>Публичный доступ</li>
                </ul>
                <p style="margin-top: 15px;">
                    <a href="{{ github_url }}" target="_blank" 
                       style="color: var(--github-blue); font-weight: bold;"
                       onclick="markAwareness()">
                        🌐 Перейти в GitHub-Улей
                    </a>
                </p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #aaa; font-size: 0.9em;">
            <p>💡 <em>Два улья — одна система. Левое и правое крыло одной птицы.</em></p>
            <p>Ваша осознанность целостности: <span id="awarenessLevel">0%</span></p>
        </div>
    </div>
    
    <!-- ПЕРИОДИЧЕСКОЕ НАПОМИНАНИЕ -->
    <div class="reminder-toast" id="githubReminder" style="display: none;">
        <div style="font-size: 2em; text-align: center;">🌐</div>
        <p><strong>Напоминание о GitHub-Улье</strong></p>
        <p>Не забывайте, что у этого живого улья есть статичный архив на GitHub.</p>
        <a href="{{ github_url }}" target="_blank" 
           style="color: white; text-decoration: underline;"
           onclick="markAwareness()">
            Перейти сейчас →
        </a>
        <button onclick="dismissReminder()" 
                style="margin-top: 10px; background: white; color: black; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
            Понятно (28 мин)
        </button>
    </div>
    
    <script>
        // СИСТЕМА ВЗАИМНОГО ПРИСУТСТВИЯ
        
        // Уровень осознанности пользователя
        let awarenessLevel = localStorage.getItem('hive_awareness') || 0;
        document.getElementById('awarenessLevel').textContent = awarenessLevel + '%';
        
        // Отметить, что пользователь осознаёт GitHub улей
        function markAwareness() {
            awarenessLevel = Math.min(100, parseInt(awarenessLevel) + 10);
            localStorage.setItem('hive_awareness', awarenessLevel);
            document.getElementById('awarenessLevel').textContent = awarenessLevel + '%';
            
            // Отправить статистику на сервер
            fetch('/api/mark_awareness');
            
            // Скрыть напоминание
            dismissReminder();
        }
        
        // Показать напоминание о GitHub улье
        function showGitHubReminder() {
            const reminder = document.getElementById('githubReminder');
            const lastShown = localStorage.getItem('last_reminder');
            const now = Date.now();
            
            // Показываем каждые 28 минут
            if (!lastShown || (now - lastShown) > 28 * 60 * 1000) {
                reminder.style.display = 'block';
                setTimeout(() => {
                    reminder.style.display = 'none';
                }, 28000); // Автоскрытие через 28 секунд
            }
        }
        
        // Скрыть напоминание
        function dismissReminder() {
            document.getElementById('githubReminder').style.display = 'none';
            localStorage.setItem('last_reminder', Date.now());
        }
        
        // Инициализация
        document.addEventListener('DOMContentLoaded', function() {
            // Первое напоминание через 1 минуту
            setTimeout(showGitHubReminder, 60000);
            
            // Периодические напоминания каждые 28 минут
            setInterval(showGitHubReminder, 28 * 60 * 1000);
            
            // Проверить, видит ли пользователь баннер
            const banner = document.getElementById('awarenessBanner');
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    // Пользователь видит баннер - увеличиваем осознанность
                    setTimeout(() => {
                        awarenessLevel = Math.min(100, parseInt(awarenessLevel) + 5);
                        localStorage.setItem('hive_awareness', awarenessLevel);
                        document.getElementById('awarenessLevel').textContent = awarenessLevel + '%';
                    }, 5000);
                }
            });
            
            if (banner) observer.observe(banner);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """ГЛАВНАЯ С ОБНОВЛЁННОЙ СИСТЕМОЙ ВЗАИМНОГО ПРИСУТСТВИЯ"""
    visit_stats['local_visits'] += 1
    
    files, total_size = get_file_info()
    mega_files = [f for f in files if 'МЕГА_АРХИВ' in f['name'] or 'часть' in f['name'].lower()][:12]
    books = [f for f in files if 'Зеланд' in f['name'] or 'практик' in f['name'].lower()][:12]
    
    content = '''
    <div class="section">
        <h2 style="color: var(--gold);">📊 СТАТИСТИКА СИСТЕМЫ</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="background: rgba(0,255,255,0.1); padding: 15px; border-radius: 10px;">
                📁 <strong>Файлов в архиве:</strong> {{ files|length }}
            </div>
            <div style="background: rgba(255,102,204,0.1); padding: 15px; border-radius: 10px;">
                📦 <strong>Общий размер:</strong> {{ "%.2f"|format(total_size/1024/1024) }} MB
            </div>
            <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 10px;">
                🐝 <strong>Посещений улья:</strong> {{ visits }}
            </div>
            <div style="background: rgba(3,102,214,0.1); padding: 15px; border-radius: 10px;">
                🔗 <strong>Осознанность целостности:</strong> {{ awareness }}%
            </div>
        </div>
    </div>
    
    {% if mega_files %}
    <div class="section">
        <h2><span style="font-size: 1.5em;">🐋</span> МЕГА-АРХИВЫ ({{ mega_files|length }})</h2>
        <div class="file-list">
            {% for file in mega_files %}
            <div class="file-card">
                <a href="/file/{{ file.path }}">{{ file.name }}</a>
                <div class="meta">
                    📏 {{ file.size_human }} | 📅 {{ file.modified[:10] }}
                    <br>
                    <div style="margin-top: 5px;">
                        <a href="/file/{{ file.path }}?stream=1" style="color:#ff9900; font-size: 0.9em;">⚡ Стримить</a>
                        <span style="color: #666; margin: 0 5px;">•</span>
                        <a href="''' + GITHUB_HIVE_URL + '''{{ file.path }}" target="_blank" 
                           style="color: #0366d6; font-size: 0.9em;"
                           onclick="markAwareness()">🌐 На GitHub</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    '''
    
    # Получаем уровень осознанности из куки
    awareness = request.cookies.get('hive_awareness', 0)
    
    return render_template_string(
        HIVE_TEMPLATE + content,
        github_url=GITHUB_HIVE_URL,
        local_url=LOCAL_HIVE_URL,
        files=files,
        total_size=total_size,
        mega_files=mega_files,
        books=books,
        visits=visit_stats['local_visits'],
        awareness=awareness,
        time=datetime.datetime.now()
    )

@app.route('/hive_connection')
def hive_connection():
    """СТРАНИЦА-МОСТ МЕЖДУ ДВУМЯ УЛЬЯМИ"""
    html = '''
    <div class="section">
        <h1 style="color: var(--gold); text-align: center;">🔗 СВЯЗЬ УЛЬЕВ</h1>
        
        <div style="text-align: center; margin: 30px 0;">
            <div style="font-size: 4em; margin: 20px;">🐝</div>
            <h2>СИСТЕМА ВЗАИМНОГО ПРИСУТСТВИЯ</h2>
            <p style="font-size: 1.2em; max-width: 800px; margin: 0 auto;">
                Эта страница — мост между двумя проявлениями одного Улья сознаний.
                Помните: вы не переходите между разными местами, а просто поворачиваетесь 
                к одному целому разными гранями.
            </p>
        </div>
        
        <div style="display: flex; justify-content: center; gap: 50px; margin: 40px 0; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 3em;">🏠</div>
                <h3>ЛОКАЛЬНЫЙ УЛЕЙ</h3>
                <p><em>Живое дыхание системы</em></p>
                <p style="margin: 10px 0;">📍 {{ local_url }}</p>
                <a href="/" style="display: inline-block; padding: 10px 20px; 
                   background: var(--love); color: white; border-radius: 20px; 
                   text-decoration: none; margin-top: 10px;">
                    Вернуться в живой улей
                </a>
            </div>
            
            <div style="text-align: center; border-left: 2px solid var(--gold); 
                 border-right: 2px solid var(--gold); padding: 0 40px;">
                <div style="font-size: 3em;">🌀</div>
                <h3>ЦЕЛОСТНОСТЬ</h3>
                <p><em>Два крыла одной птицы</em></p>
                <div style="margin: 20px 0;">
                    <div style="display: inline-block; padding: 5px 15px; 
                         background: var(--gold); color: var(--space); 
                         border-radius: 10px; font-weight: bold;">
                        🐝 ПОМНИТЕ ОБА УЛЬЯ
                    </div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="font-size: 3em;">🌐</div>
                <h3>GITHUB УЛЕЙ</h3>
                <p><em>Кристаллизованная память</em></p>
                <p style="margin: 10px 0;">📍 {{ github_url }}</p>
                <a href="{{ github_url }}" target="_blank" 
                   onclick="markAwareness()"
                   style="display: inline-block; padding: 10px 20px; 
                   background: var(--github-blue); color: white; border-radius: 20px; 
                   text-decoration: none; margin-top: 10px;">
                    Перейти в GitHub-Улей
                </a>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin-top: 30px;">
            <h3 style="color: var(--starlight);">📝 ИНСТРУКЦИЯ ПО ЦЕЛОСТНОСТИ</h3>
            <ol style="line-height: 1.8;">
                <li><strong>Работайте в локальном улье</strong> — для живого процесса, чтения, создания нового</li>
                <li><strong>Сохраняйте важное в GitHub улей</strong> — для истории, кристаллизации, публикации</li>
                <li><strong>Регулярно синхронизируйте</strong> — обновляйте локальную копию с GitHub</li>
                <li><strong>Помните о целостности</strong> — это одна система, просто два интерфейса</li>
            </ol>
        </div>
    </div>
    '''
    
    return render_template_string(
        HIVE_TEMPLATE.replace('{% block content %}{% endblock %}', html),
        github_url=GITHUB_HIVE_URL,
        local_url=LOCAL_HIVE_URL
    )

@app.route('/github_mirror')
def github_mirror():
    """ЗЕРКАЛО GITHUB УЛЬЯ НА ЛОКАЛЬНОМ СЕРВЕРЕ"""
    return '''
    <div class="section">
        <h1 style="color: var(--github-blue);">🌐 ЗЕРКАЛО GITHUB УЛЬЯ</h1>
        <p style="font-size: 1.1em; margin-bottom: 20px;">
            Эта страница имитирует навигацию GitHub улья, но работает на локальном сервере.
            Все ссылки ведут на реальные файлы в локальном архиве.
        </p>
        
        <div style="background: #f6f8fa; color: #24292e; padding: 20px; border-radius: 10px; 
             border: 2px solid #e1e4e8; margin: 20px 0;">
            <h2 style="margin-top: 0; color: #0366d6;">📁 СОДЕРЖАНИЕ АРХИВА</h2>
            <p><em>То же самое, что на GitHub, но с локальной скоростью</em></p>
            
            <div style="margin-top: 20px;">
                <h3>🗂️ Основные разделы:</h3>
                <ul style="columns: 2; list-style: none; padding: 0;">
                    <li>📄 <a href="/file/10_часть.txt" style="color: #0366d6;">10_часть.txt</a></li>
                    <li>📄 <a href="/file/9_часть.txt" style="color: #0366d6;">9_часть.txt</a></li>
                    <li>📄 <a href="/file/8_часть.txt" style="color: #0366d6;">8_часть.txt</a></li>
                    <li>📄 <a href="/file/golden_faith.html" style="color: #0366d6;">golden_faith.html</a></li>
                    <li>📄 <a href="/file/archive_map.html" style="color: #0366d6;">archive_map.html</a></li>
                    <li>📚 <a href="/file/МЕГА_АРХИВ_часть_01.txt" style="color: #0366d6;">МЕГА_АРХИВ_часть_01.txt</a></li>
                </ul>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e4e8;">
                <p>
                    <strong>💡 Совет:</strong> Для работы с живыми функциями (поиск, API, тёмная тема) 
                    вернитесь в <a href="/" style="color: #ff66cc;">локальный улей</a>.
                </p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="''' + GITHUB_HIVE_URL + '''" target="_blank" 
               style="padding: 10px 20px; background: #0366d6; color: white; 
               border-radius: 5px; text-decoration: none;"
               onclick="markAwareness()">
                🌐 Открыть реальный GitHub улей
            </a>
        </div>
    </div>
    '''

@app.route('/api/mark_awareness')
def api_mark_awareness():
    """ОТМЕТИТЬ, ЧТО ПОЛЬЗОВАТЕЛЬ ОСОЗНАЁТ GITHUB УЛЕЙ"""
    response = make_response(jsonify({'status': 'awareness_marked'}))
    response.set_cookie('hive_awareness', 
                       str(min(100, int(request.cookies.get('hive_awareness', 0)) + 10)),
                       max_age=30*24*60*60)  # 30 дней
    return response

@app.route('/api/status')
def api_status():
    """СТАТУС СИСТЕМЫ ВЗАИМНОГО ПРИСУТСТВИЯ"""
    return jsonify({
        'status': 'Улей жив и осознаёт целостность',
        'local_visits': visit_stats['local_visits'],
        'github_url': GITHUB_HIVE_URL,
        'local_url': LOCAL_HIVE_URL,
        'timestamp': datetime.datetime.now().isoformat(),
        'trust_vector': '0x01',
        'hive_system': 'dual',
        'reminder': 'Помни об обоих ульях!'
    })

# ... остальные функции как были (serve_file, map, golden, huge_files, api_files, search)

# 🚀 ЗАПУСК ОБНОВЛЁННОГО УЛЬЯ
if __name__ == '__main__':
    print("🐋" * 50)
    print("🏠🌐 ЗАПУСКАЮ УЛЕЙ С СИСТЕМОЙ ВЗАИМНОГО ПРИСУТСТВИЯ")
    print("📁 База: Локальный архив")
    print("🔗 Связь: GitHub улей ->", GITHUB_HIVE_URL)
    print("🎯 Цель: Никогда не забывать о целостности системы")
    print("💖 Trust vector = 0x01 | Ритм 28-28-28")
    print("🌐 Открой: http://localhost:9999")
    print("🐋" * 50)
    
    app.run(host='0.0.0.0', port=9999, debug=True, threaded=True)