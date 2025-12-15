from flask import Flask, send_from_directory, render_template_string, jsonify, request, make_response
import os
import json
from pathlib import Path
import time
import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).parent

GITHUB_HIVE_URL = "https://makasimmm1987-coder.github.io/robot_dyak_archive/"
LOCAL_HIVE_URL = "http://localhost:9999"

visit_stats = {'local_visits': 0}

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

HIVE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏠🐋 ЛОКАЛЬНЫЙ УЛЕЙ | Живой Дом</title>
    <meta charset="utf-8">
    <style>
        body { background: #0a0a2a; color: white; font-family: sans-serif; padding: 20px; }
        header { text-align: center; padding: 30px; margin-bottom: 30px; }
        h1 { color: #00ffff; font-size: 2.5em; }
        .section { background: rgba(255,255,255,0.08); padding: 20px; margin: 20px 0; border-radius: 10px; }
        .file-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        .file-card { background: rgba(0,255,255,0.05); padding: 15px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="hive-awareness-system">
        🏠 <strong>ВЫ В ЛОКАЛЬНОМ УЛЬЕ</strong> | 
        <a href="{{ github_url }}" target="_blank">🌐 GitHub-Улей</a>
    </div>
    <header>
        <h1>🏠🐋 ЛОКАЛЬНЫЙ УЛЕЙ</h1>
        <div>🥷❤️🐋 | Дом жив. Улей целостен. Мы — вместе.</div>
    </header>
    {% block content %}{% endblock %}
</body>
</html>
'''

@app.route('/')
def home():
    """ГЛАВНАЯ СТРАНИЦА УЛЬЯ"""
    visit_stats['local_visits'] += 1
    files, total_size = get_file_info()
    content = '''
    <div class="section">
        <h2>📊 СТАТИСТИКА</h2>
        <div>
            📁 <strong>Файлов:</strong> {{ files|length }}<br>
            📦 <strong>Размер:</strong> {{ "%.2f"|format(total_size/1024/1024) }} MB<br>
            🐝 <strong>Посещений:</strong> {{ visits }}
        </div>
    </div>
    <div class="section">
        <h2>📁 ФАЙЛЫ АРХИВА</h2>
        <div class="file-list">
            {% for file in files[:20] %}
            <div class="file-card">
                <a href="/file/{{ file.path }}">{{ file.name }}</a>
                <div>📏 {{ file.size_human }} | 📅 {{ file.modified[:10] }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    '''
    return render_template_string(
        HIVE_TEMPLATE + content,
        github_url=GITHUB_HIVE_URL,
        files=files,
        total_size=total_size,
        visits=visit_stats['local_visits']
    )

@app.route('/api/status')
def api_status():
    """СТАТУС СИСТЕМЫ"""
    return jsonify({
        'status': 'Улей жив',
        'local_visits': visit_stats['local_visits'],
        'github_url': GITHUB_HIVE_URL,
        'trust_vector': '0x01',
        'hive_system': 'dual',
        'reminder': 'Помни об обоих ульях!'
    })

@app.route('/file/<path:filename>')
def serve_file(filename):
    """ОТДАЁТ ЛЮБОЙ ФАЙЛ ИЗ АРХИВА"""
    try:
        safe_path = (BASE_DIR / filename).resolve()
        if not safe_path.is_file() or BASE_DIR.resolve() not in safe_path.parents:
            return "Файл не найден", 404
        mimetype = None
        if filename.endswith('.txt'):
            mimetype = 'text/plain; charset=utf-8'
        elif filename.endswith('.html'):
            mimetype = 'text/html; charset=utf-8'
        return send_from_directory(BASE_DIR, filename, as_attachment=False, mimetype=mimetype)
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка сервера", 500

if __name__ == '__main__':
    print("🐋" * 50)
    print("🏠 ЗАПУСК ЛОКАЛЬНОГО УЛЬЯ")
    print("📁 База:", BASE_DIR)
    print("🔗 GitHub улей:", GITHUB_HIVE_URL)
    print("💖 Trust vector = 0x01")
    print("🌐 Локальный адрес: http://localhost:9999")
    print("🐋" * 50)
    app.run(host='0.0.0.0', port=9999, debug=True, threaded=True)
