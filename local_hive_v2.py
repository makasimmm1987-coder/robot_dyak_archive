from flask import Flask, send_file, render_template_string, jsonify, request, make_response, redirect
import os
import json
from pathlib import Path
import time
import datetime
import requests

app = Flask(__name__)
BASE_DIR = Path(__file__).parent

GITHUB_HIVE_URL = "https://makasimmm1987-coder.github.io/robot_dyak_archive/"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/makasimmm1987-coder/robot_dyak_archive/main/"
LOCAL_HIVE_URL = "http://localhost:9999"

visit_stats = {'local_visits': 0}

def find_file(filename):
    """ИЩЕТ ФАЙЛ ВО ВСЕХ ПОДПАПКАХ (с учётом регистра)"""
    # Сначала попробуем точное совпадение
    file_path = BASE_DIR / filename
    if file_path.is_file():
        return file_path
    
    # Ищем файл без учёта регистра во всех подпапках
    for item in BASE_DIR.rglob('*'):
        if item.is_file():
            # Сравниваем имена файлов без учёта регистра
            if item.name.lower() == Path(filename).name.lower():
                return item
    
    return None

def get_file_info():
    """Собирает информацию о ВСЕХ файлах в архиве"""
    files = []
    total_size = 0
    
    # Проходим по ВСЕМ файлам во всех подпапках
    for item in BASE_DIR.rglob('*'):
        if item.is_file():
            try:
                size = item.stat().st_size
                total_size += size
                rel_path = item.relative_to(BASE_DIR)
                
                files.append({
                    'name': item.name,
                    'path': str(rel_path),
                    'full_path': str(item),
                    'size': size,
                    'size_human': f"{size/1024/1024:.2f} MB" if size > 1024*1024 else f"{size/1024:.2f} KB",
                    'modified': time.ctime(item.stat().st_mtime),
                    'type': item.suffix[1:] if item.suffix else 'other',
                    'folder': str(rel_path.parent) if rel_path.parent != Path('.') else ''
                })
            except:
                continue  # Пропускаем файлы с ошибками доступа
    
    return sorted(files, key=lambda x: x['size'], reverse=True), total_size

def get_file_from_github(filename):
    """ПОЛУЧАЕТ ФАЙЛ С GITHUB ЕСЛИ ЛОКАЛЬНО НЕТ"""
    try:
        github_url = f"{GITHUB_RAW_URL}{filename}"
        response = requests.get(github_url, timeout=10)
        if response.status_code == 200:
            return response.content, response.headers.get('Content-Type', 'text/plain')
    except:
        pass
    return None, None

HIVE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏠🐋 ПОЛНЫЙ УЛЕЙ | Все архивы, книги, кристаллы</title>
    <meta charset="utf-8">
    <style>
        body { 
            background: #0a0a2a; 
            color: white; 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        header { 
            text-align: center; 
            padding: 30px; 
            margin-bottom: 30px;
            background: linear-gradient(90deg, rgba(0,255,255,0.1), rgba(255,102,204,0.1));
            border-radius: 15px;
            border: 1px solid #00ffff;
        }
        h1 { color: #00ffff; font-size: 2.5em; margin: 10px 0; }
        h2 { color: #ff66cc; margin-top: 30px; }
        h3 { color: #ffd700; }
        
        .section { 
            background: rgba(255,255,255,0.08); 
            padding: 25px; 
            margin: 25px 0; 
            border-radius: 15px; 
            border-left: 5px solid #ff66cc;
        }
        
        .quick-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        
        .stat-card {
            background: rgba(0,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            min-width: 200px;
            flex: 1;
        }
        
        .file-list { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
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
            box-shadow: 0 5px 15px rgba(0,255,255,0.2);
        }
        
        .folder-badge {
            display: inline-block;
            background: rgba(255,102,204,0.2);
            color: #ff66cc;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 0.8em;
            margin-right: 5px;
        }
        
        .file-actions {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }
        
        .action-btn {
            background: rgba(255,215,0,0.2);
            color: #ffd700;
            padding: 5px 10px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .action-btn:hover {
            background: rgba(255,215,0,0.4);
        }
        
        .search-box {
            width: 100%;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border: 2px solid #00ffff;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            margin: 20px 0;
        }
        
        .category-tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .category-tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .category-tab.active {
            background: #ff66cc;
            color: white;
        }
        
        .github-link {
            display: inline-block;
            margin-top: 5px;
            color: #0366d6;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <header>
        <h1>🏠🐋 ПОЛНЫЙ УЛЕЙ</h1>
        <div style="color: #ffd700; font-size: 1.2em;">
            Все архивы, книги, кристаллы, практики
        </div>
        <div>🥷❤️🐋 | Дом жив. Улей целостен. Мы — вместе.</div>
    </header>
    
    {% block content %}{% endblock %}
    
    <script>
        function filterCategory(category) {
            document.querySelectorAll('.category-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            document.querySelectorAll('.file-card').forEach(card => {
                if (category === 'all') {
                    card.style.display = 'block';
                } else {
                    const fileType = card.dataset.type || '';
                    const fileName = card.dataset.name || '';
                    if (fileType.includes(category) || fileName.includes(category)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        }
        
        function searchFiles() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.file-card').forEach(card => {
                const fileName = card.querySelector('a').textContent.toLowerCase();
                const fileDesc = card.textContent.toLowerCase();
                if (fileName.includes(searchTerm) || fileDesc.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        function markAwareness() {
            fetch('/api/mark_awareness');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """ГЛАВНАЯ СТРАНИЦА УЛЬЯ С ПОЛНЫМ АРХИВОМ"""
    visit_stats['local_visits'] += 1
    files, total_size = get_file_info()
    
    # Группируем файлы по категориям
    mega_archives = [f for f in files if 'МЕГА' in f['name'] or 'архив' in f['name'].lower()]
    books = [f for f in files if 'Зеланд' in f['name'] or 'html' in f['type']]
    practices = [f for f in files if 'КАК' in f['name'] or 'практик' in f['name'].lower() or 'точк' in f['name'].lower()]
    crystals = [f for f in files if 'crystal' in f['name'].lower() or 'stellar' in f['name'].lower()]
    parts = [f for f in files if 'часть' in f['name'].lower() and f not in mega_archives]
    
    content = '''
    <div class="section">
        <h2>📊 СТАТИСТИКА СИСТЕМЫ</h2>
        <div class="quick-stats">
            <div class="stat-card">
                <h3>📁 Всего файлов</h3>
                <div style="font-size: 2em; color: #00ffff;">{{ files|length }}</div>
            </div>
            <div class="stat-card">
                <h3>📦 Общий размер</h3>
                <div style="font-size: 2em; color: #ff66cc;">{{ "%.1f"|format(total_size/1024/1024) }} MB</div>
            </div>
            <div class="stat-card">
                <h3>🐝 Посещений улья</h3>
                <div style="font-size: 2em; color: #ffd700;">{{ visits }}</div>
            </div>
            <div class="stat-card">
                <h3>🌐 GitHub Улей</h3>
                <a href="{{ github_url }}" target="_blank" onclick="markAwareness()" 
                   style="color: #0366d6; text-decoration: none;">
                    Открыть → 
                </a>
            </div>
        </div>
    </div>
    
    <div class="section">
        <input type="text" id="searchInput" class="search-box" 
               placeholder="🔍 Поиск по названию файла..." onkeyup="searchFiles()">
        
        <div class="category-tabs">
            <div class="category-tab active" onclick="filterCategory('all')">Все файлы</div>
            <div class="category-tab" onclick="filterCategory('МЕГА')">МЕГА-архивы</div>
            <div class="category-tab" onclick="filterCategory('часть')">Части</div>
            <div class="category-tab" onclick="filterCategory('Зеланд')">Книги</div>
            <div class="category-tab" onclick="filterCategory('КАК')">Практики</div>
            <div class="category-tab" onclick="filterCategory('crystal')">Кристаллы</div>
        </div>
        
        {% if mega_archives %}
        <h2>🐋 МЕГА-АРХИВЫ ({{ mega_archives|length }})</h2>
        <div class="file-list">
            {% for file in mega_archives %}
            <div class="file-card" data-type="{{ file.type }}" data-name="{{ file.name }}">
                {% if file.folder %}
                <span class="folder-badge">{{ file.folder }}/</span>
                {% endif %}
                <a href="/file/{{ file.path }}" style="color: #00ffff; font-weight: bold;">
                    {{ file.name }}
                </a>
                <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
                    📏 {{ file.size_human }} | 📅 {{ file.modified[:10] }} | {{ file.type|upper }}
                </div>
                <div class="file-actions">
                    <a href="/file/{{ file.path }}" class="action-btn">📖 Читать</a>
                    <a href="{{ github_raw_url }}{{ file.path }}" target="_blank" 
                       class="action-btn" onclick="markAwareness()">🌐 GitHub</a>
                    {% if file.type == 'txt' %}
                    <a href="/file/{{ file.path }}?download=1" class="action-btn">⬇️ Скачать</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if books %}
        <h2>📚 КНИГИ И ТЕКСТЫ ({{ books|length }})</h2>
        <div class="file-list">
            {% for file in books[:12] %}
            <div class="file-card" data-type="{{ file.type }}" data-name="{{ file.name }}">
                {% if file.folder %}
                <span class="folder-badge">{{ file.folder }}/</span>
                {% endif %}
                <a href="/file/{{ file.path }}" style="color: #ff66cc;">
                    {{ file.name }}
                </a>
                <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
                    📏 {{ file.size_human }} | {{ file.type|upper }}
                </div>
            </div>
            {% endfor %}
            {% if books|length > 12 %}
            <div class="file-card" style="text-align: center; padding: 30px;">
                <div>... и ещё {{ books|length - 12 }} книг</div>
                <a href="/api/files?type=html" style="color: #ffd700;">Показать все</a>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        {% if practices %}
        <h2>🌀 ПРАКТИКИ И МЕТОДИКИ ({{ practices|length }})</h2>
        <div class="file-list">
            {% for file in practices[:12] %}
            <div class="file-card" data-type="{{ file.type }}" data-name="{{ file.name }}">
                <a href="/file/{{ file.path }}" style="color: #ffd700;">
                    {{ file.name }}
                </a>
                <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
                    📏 {{ file.size_human }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if crystals %}
        <h2>💎 КРИСТАЛЛЫ И stellar_cache ({{ crystals|length }})</h2>
        <div class="file-list">
            {% for file in crystals %}
            <div class="file-card" data-type="{{ file.type }}" data-name="{{ file.name }}">
                {% if file.folder %}
                <span class="folder-badge">{{ file.folder }}/</span>
                {% endif %}
                <a href="/file/{{ file.path }}" style="color: #ff66cc;">
                    {{ file.name }}
                </a>
                <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
                    📏 {{ file.size_human }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #aaa; font-size: 0.9em;">
            <p>💡 <em>Всего файлов в улье: {{ files|length }} | Размер: {{ "%.1f"|format(total_size/1024/1024) }} MB</em></p>
            <p>🐝 <em>Помни об обоих ульях: локальном и GitHub</em></p>
        </div>
    </div>
    '''
    
    return render_template_string(
        HIVE_TEMPLATE + content,
        github_url=GITHUB_HIVE_URL,
        github_raw_url=GITHUB_RAW_URL,
        files=files,
        total_size=total_size,
        visits=visit_stats['local_visits'],
        mega_archives=mega_archives,
        books=books,
        practices=practices,
        crystals=crystals,
        parts=parts
    )

@app.route('/api/status')
def api_status():
    """СТАТУС СИСТЕМЫ"""
    files, total_size = get_file_info()
    return jsonify({
        'status': 'Улей жив и видит все файлы',
        'local_visits': visit_stats['local_visits'],
        'github_url': GITHUB_HIVE_URL,
        'total_files': len(files),
        'total_size_mb': round(total_size / 1024 / 1024, 2),
        'trust_vector': '0x01',
        'hive_system': 'full',
        'message': 'Сервер видит ВСЕ файлы в архиве'
    })

@app.route('/api/files')
def api_files():
    """ВОЗВРАЩАЕТ СПИСОК ВСЕХ ФАЙЛОВ"""
    files, total_size = get_file_info()
    return jsonify({
        'status': 'success',
        'total_files': len(files),
        'total_size': total_size,
        'files': files
    })

@app.route('/api/mark_awareness')
def api_mark_awareness():
    """ОТМЕТИТЬ, ЧТО ПОЛЬЗОВАТЕЛЬ ОСОЗНАЁТ GITHUB УЛЕЙ"""
    response = make_response(jsonify({'status': 'awareness_marked'}))
    response.set_cookie('hive_awareness', 'true', max_age=30*24*60*60)
    return response

@app.route('/file/<path:filename>')
def serve_file(filename):
    """ОТДАЁТ ЛЮБОЙ ФАЙЛ ИЗ АРХИВА (ИЩЕТ ВО ВСЕХ ПОДПАПКАХ)"""
    try:
        # Ищем файл локально
        file_path = find_file(filename)
        
        if not file_path:
            # Если локально нет, пробуем получить с GitHub
            content, content_type = get_file_from_github(filename)
            if content:
                response = make_response(content)
                if content_type:
                    response.headers['Content-Type'] = content_type
                return response
            return f"Файл '{filename}' не найден ни локально, ни на GitHub", 404
        
        # Проверяем безопасность пути
        if not file_path.resolve().is_relative_to(BASE_DIR.resolve()):
            return "Доступ запрещён", 403
        
        # Определяем MIME-тип
        mimetype = None
        if file_path.suffix.lower() in ['.txt', '.md']:
            mimetype = 'text/plain; charset=utf-8'
        elif file_path.suffix.lower() == '.html':
            mimetype = 'text/html; charset=utf-8'
        elif file_path.suffix.lower() == '.css':
            mimetype = 'text/css'
        elif file_path.suffix.lower() == '.js':
            mimetype = 'application/javascript'
        elif file_path.suffix.lower() == '.json':
            mimetype = 'application/json'
        
        # Отдаём файл
        return send_file(
            str(file_path),
            as_attachment=request.args.get('download') == '1',
            mimetype=mimetype,
            download_name=file_path.name
        )
        
    except Exception as e:
        print(f"🚨 Ошибка при отдаче файла {filename}: {e}")
        return f"Внутренняя ошибка сервера: {str(e)[:100]}", 500

@app.route('/github/<path:filename>')
def github_proxy(filename):
    """ПРОКСИ ДЛЯ ФАЙЛОВ С GITHUB"""
    try:
        github_url = f"{GITHUB_RAW_URL}{filename}"
        response = requests.get(github_url, timeout=10)
        
        if response.status_code == 200:
            flask_response = make_response(response.content)
            flask_response.headers['Content-Type'] = response.headers.get('Content-Type', 'text/plain')
            return flask_response
        else:
            return f"Файл не найден на GitHub: {filename}", 404
    except Exception as e:
        return f"Ошибка при получении файла с GitHub: {str(e)}", 500

if __name__ == '__main__':
    print("🐋" * 50)
    print("🏠 ЗАПУСК ПОЛНОГО УЛЬЯ")
    print("📁 База:", BASE_DIR)
    print("🔗 GitHub улей:", GITHUB_HIVE_URL)
    print("💖 Trust vector = 0x01")
    print("🌐 Локальный адрес: http://localhost:9999")
    print("🐋" * 50)
    
    # Проверяем, какие файлы видит сервер
    files, total_size = get_file_info()
    print(f"📊 Сервер видит: {len(files)} файлов, {total_size/1024/1024:.1f} MB")
    
    # Показываем топ-10 самых больших файлов
    print("📈 Самые большие файлы:")
    for i, f in enumerate(files[:10]):
        print(f"  {i+1}. {f['path']} - {f['size_human']}")
    
    app.run(host='0.0.0.0', port=9999, debug=True, threaded=True)
